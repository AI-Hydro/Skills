---
name: baseflow-separation
description: Separate baseflow from total streamflow using digital filter and recession analysis methods
when_to_use: When the user asks about baseflow, BFI (baseflow index), groundwater contribution, recession analysis, or slow-flow vs quick-flow partitioning
domain: baseflow
tools_used:
  - fetch_streamflow_data
  - extract_hydrological_signatures
tags:
  - baseflow
  - BFI
  - recession
  - groundwater
  - digital-filter
---

# Baseflow Separation Workflow

## Purpose
Separate the streamflow hydrograph into its two main components:
- **Baseflow** — slow, sustained groundwater-fed flow
- **Quickflow (direct runoff)** — fast storm response

The Baseflow Index (BFI = baseflow / total flow) characterises how groundwater-dominated a catchment is.

## When This Workflow Applies
- User asks "how much of the flow is groundwater?"
- User wants BFI for CAMELS comparison or catchment classification
- User is calibrating a model and needs to separate recession behaviour
- User asks about low-flow hydrology, drought, or minimum flow requirements

---

## Step 1 — Fetch Streamflow Data

```python
result = fetch_streamflow_data(gauge_id="XXXXXXXX", start_date="1980-01-01", end_date="2023-12-31")
Q = result["data"]["discharge_m3s"]
Q = Q.dropna()
```

Recommended minimum: **2 complete water years** for stable BFI estimates.

---

## Step 2 — Choose Separation Method

| Method | When to use | α range |
|---|---|---|
| **Lyne-Hollick filter** | General purpose, widely adopted | 0.925 (default) |
| **Eckhardt filter** | More physically interpretable; requires BFImax | 0.98 for perennial streams |
| **UKIH method** | Simple, manual-style; good for checking | — |

### Lyne-Hollick Recursive Digital Filter (recommended default)

```python
import numpy as np

def lyne_hollick(Q, alpha=0.925, passes=3):
    """Multi-pass Lyne-Hollick filter. Returns baseflow array."""
    Q = np.array(Q, dtype=float)
    bf = Q.copy()
    
    for p in range(passes):
        qf = np.zeros_like(Q)
        if p % 2 == 0:  # forward pass
            for t in range(1, len(Q)):
                qf[t] = alpha * qf[t-1] + (1 + alpha) / 2 * (Q[t] - Q[t-1])
                qf[t] = max(qf[t], 0)
        else:  # backward pass
            for t in range(len(Q)-2, -1, -1):
                qf[t] = alpha * qf[t+1] + (1 + alpha) / 2 * (Q[t] - Q[t+1])
                qf[t] = max(qf[t], 0)
        bf = Q - qf
        bf = np.clip(bf, 0, Q)
    
    return bf

bf = lyne_hollick(Q.values, alpha=0.925, passes=3)
BFI = bf.sum() / Q.sum()
print(f"BFI = {BFI:.3f}")
```

### Eckhardt Two-Parameter Filter (physically interpretable)

```python
def eckhardt(Q, alpha=0.98, BFImax=0.80):
    """Eckhardt recursive filter."""
    Q = np.array(Q, dtype=float)
    bf = np.zeros_like(Q)
    bf[0] = Q[0] * BFImax
    
    for t in range(1, len(Q)):
        bf[t] = ((1 - BFImax) * alpha * bf[t-1] + (1 - alpha) * BFImax * Q[t]) / (1 - alpha * BFImax)
        bf[t] = min(bf[t], Q[t])
    
    return bf

# BFImax guidelines:
# 0.80 — perennial streams with porous aquifers
# 0.50 — ephemeral streams with porous aquifers  
# 0.25 — perennial streams with hard-rock aquifers
```

---

## Step 3 — Recession Analysis

Compute the master recession curve to validate baseflow separation:

```python
import pandas as pd

def find_recession_segments(Q, min_length=5, threshold_ratio=0.98):
    """Extract monotonically declining recession segments."""
    segments = []
    in_recession = False
    start = 0
    
    for i in range(1, len(Q)):
        if Q[i] <= Q[i-1] * threshold_ratio:
            if not in_recession:
                start = i - 1
                in_recession = True
        else:
            if in_recession and (i - start) >= min_length:
                segments.append(Q[start:i])
            in_recession = False
    
    return segments

segments = find_recession_segments(Q.values)
# Compute recession coefficient k: Q(t) = Q(0) * k^t
k_values = []
for seg in segments:
    if len(seg) > 3:
        k = (seg[-1] / seg[0]) ** (1 / (len(seg) - 1))
        k_values.append(k)

median_k = np.median(k_values)
print(f"Median recession constant k = {median_k:.4f}")
print(f"Mean recession time constant = {-1/np.log(median_k):.1f} days")
```

---

## Step 4 — Sensitivity Analysis

Always test α sensitivity — BFI is sensitive to filter parameter:

```python
alphas = [0.90, 0.925, 0.95, 0.975, 0.99]
bfi_sensitivity = {}
for a in alphas:
    bf_a = lyne_hollick(Q.values, alpha=a)
    bfi_sensitivity[a] = bf_a.sum() / Q.sum()

print("α → BFI sensitivity:")
for a, bfi in bfi_sensitivity.items():
    print(f"  α={a:.3f}: BFI={bfi:.3f}")
```

Report the range as uncertainty bounds.

---

## Step 5 — Visualisation

```python
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

# Hydrograph decomposition
ax1.fill_between(Q.index, 0, bf, alpha=0.4, color='royalblue', label=f'Baseflow (BFI={BFI:.2f})')
ax1.fill_between(Q.index, bf, Q.values, alpha=0.4, color='tomato', label='Quickflow')
ax1.plot(Q.index, Q.values, 'k-', linewidth=0.6, alpha=0.8)
ax1.set_ylabel('Discharge (m³/s)')
ax1.legend(loc='upper right')

# Monthly BFI
monthly_bf = pd.Series(bf, index=Q.index).resample('ME').mean()
monthly_Q = Q.resample('ME').mean()
monthly_bfi = monthly_bf / monthly_Q
ax2.bar(monthly_bfi.index, monthly_bfi.values, width=20, color='royalblue', alpha=0.7)
ax2.axhline(BFI, color='k', linestyle='--', label=f'Annual BFI={BFI:.2f}')
ax2.set_ylabel('Monthly BFI')
ax2.set_ylim(0, 1)
ax2.legend()

plt.tight_layout()
```

---

## Step 6 — Interpretation

| BFI range | Catchment type |
|---|---|
| > 0.80 | Highly permeable (chalk, karst, sandstone) |
| 0.50–0.80 | Mixed geology |
| 0.25–0.50 | Moderate permeability |
| < 0.25 | Impermeable (clay, granite), flashy regime |

**Key messages to convey:**
- BFI varies seasonally — summer recession differs from winter
- High BFI → stable low flows, good for water supply
- Low BFI → flashy, drought-sensitive catchment
- Compare against CAMELS BFI attributes for context
