---
name: calibration-diagnostics
description: Diagnose hydrological model calibration quality using NSE, KGE, FDC matching, and residual analysis; identify structural deficiencies
when_to_use: When the user has run a model and wants to evaluate its performance, asks "is my calibration good?", or wants to improve a poorly fitting simulation
domain: modelling
tools_used:
  - get_model_results
  - fetch_streamflow_data
tags:
  - calibration
  - NSE
  - KGE
  - FDC
  - diagnostics
  - model-evaluation
---

# Calibration Diagnostics Workflow

## Purpose
Evaluate whether a calibrated rainfall-runoff model is fit for purpose. Go beyond a single NSE score — understand *where* the model fails and *why*.

## When This Workflow Applies
- User ran `train_hydro_model` and wants to interpret results
- User has NSE/KGE values and asks if they're "good enough"
- Model performs poorly and user wants to fix it
- User is preparing a model for publication or operational use

---

## Step 1 — Retrieve Results

```python
results = get_model_results(session_id="current")
Q_obs = results["Q_obs"]    # observed discharge
Q_sim = results["Q_sim"]    # simulated discharge
dates = results["dates"]
```

---

## Step 2 — Compute Core Metrics

Always report all four; NSE alone is insufficient.

```python
import numpy as np

def nse(obs, sim):
    """Nash-Sutcliffe Efficiency. Range: -∞ to 1. Good: > 0.65."""
    return 1 - np.sum((obs - sim)**2) / np.sum((obs - np.mean(obs))**2)

def kge(obs, sim):
    """Kling-Gupta Efficiency. Range: -∞ to 1. Good: > 0.65."""
    r = np.corrcoef(obs, sim)[0, 1]
    alpha = np.std(sim) / np.std(obs)
    beta = np.mean(sim) / np.mean(obs)
    return 1 - np.sqrt((r - 1)**2 + (alpha - 1)**2 + (beta - 1)**2)

def pbias(obs, sim):
    """Percent bias. Good: |PBIAS| < 10%."""
    return 100 * (np.sum(sim - obs) / np.sum(obs))

def nse_log(obs, sim):
    """Log-NSE: emphasises low-flow performance."""
    eps = np.percentile(obs[obs > 0], 1)
    return nse(np.log(obs + eps), np.log(sim + eps))

metrics = {
    "NSE": nse(Q_obs, Q_sim),
    "KGE": kge(Q_obs, Q_sim),
    "PBIAS (%)": pbias(Q_obs, Q_sim),
    "NSE_log": nse_log(Q_obs, Q_sim),
}
print(metrics)
```

### Performance Benchmarks

| Metric | Poor | Satisfactory | Good | Excellent |
|---|---|---|---|---|
| NSE | < 0.5 | 0.5–0.65 | 0.65–0.75 | > 0.75 |
| KGE | < 0.5 | 0.5–0.65 | 0.65–0.75 | > 0.75 |
| \|PBIAS\| | > 25% | 15–25% | 5–15% | < 5% |
| NSE_log | < 0.4 | 0.4–0.6 | 0.6–0.75 | > 0.75 |

---

## Step 3 — Flow Duration Curve Matching

A single NSE can hide systematic FDC errors:

```python
import matplotlib.pyplot as plt

def fdc(Q, exceedance=True):
    sorted_Q = np.sort(Q)[::-1]
    prob = np.arange(1, len(Q)+1) / (len(Q)+1)
    return prob, sorted_Q

p_obs, fdc_obs = fdc(Q_obs)
p_sim, fdc_sim = fdc(Q_sim)

fig, ax = plt.subplots(figsize=(9, 5))
ax.semilogy(p_obs * 100, fdc_obs, 'k-', linewidth=2, label='Observed')
ax.semilogy(p_sim * 100, fdc_sim, 'r--', linewidth=2, label='Simulated')
ax.set_xlabel('Exceedance probability (%)')
ax.set_ylabel('Discharge (m³/s)')
ax.legend()
ax.grid(True, which='both', alpha=0.3)
```

**What to look for in the FDC:**

| FDC region | Exceedance % | Represents | Common error |
|---|---|---|---|
| High flows | 0–10% | Flood peaks | Over/underestimation → wrong BETA / routing |
| Mid-range | 10–70% | Average conditions | Bias → water balance error |
| Low flows | 70–99% | Baseflow / drought | NSE_log error → K2 or groundwater storage |

---

## Step 4 — Residual Analysis

```python
import pandas as pd

residuals = Q_sim - Q_obs
df = pd.DataFrame({'date': dates, 'Q_obs': Q_obs, 'Q_sim': Q_sim, 'residual': residuals})
df = df.set_index('date')

# Seasonal decomposition of residuals
monthly_bias = df['residual'].resample('ME').mean()
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Time series
axes[0].plot(df.index, df['Q_obs'], 'k-', alpha=0.7, label='Obs')
axes[0].plot(df.index, df['Q_sim'], 'r-', alpha=0.7, label='Sim')
axes[0].legend(); axes[0].set_ylabel('Q (m³/s)')

# Monthly residuals
monthly_bias.plot(kind='bar', ax=axes[1], color='steelblue')
axes[1].axhline(0, color='k'); axes[1].set_ylabel('Mean monthly bias')

# Scatter
axes[2].scatter(df['Q_obs'], df['Q_sim'], alpha=0.2, s=5)
lim = max(df['Q_obs'].max(), df['Q_sim'].max())
axes[2].plot([0, lim], [0, lim], 'k--')
axes[2].set_xlabel('Q_obs'); axes[2].set_ylabel('Q_sim')

plt.tight_layout()
```

---

## Step 5 — Diagnose Failure Modes

Use this table to connect metric patterns to model deficiencies:

| Symptom | Likely cause | Fix |
|---|---|---|
| High NSE, high PBIAS | Volume error | Adjust ET parameter (LP, BETA) |
| Good mid-range, poor peaks | Under-routing | Reduce MAXBAS (HBV) |
| Good peaks, poor low flows | Poor recession | Adjust K2, PERC |
| Seasonal bias (wet bias in winter) | Missing snowmelt | Add/tune snow routine |
| Large scatter, low NSE | Forcing error or wrong area | Check P inputs, gauge area |
| KGE << NSE | Flow variability wrong | α component: adjust storage parameters |

---

## Step 6 — Split-Sample Test

Always validate on an independent period:

```python
# Recommended split: 
# Warm-up: 2 years (model spin-up, not evaluated)
# Calibration: 60% of remaining record
# Validation: 40% of remaining record

# Satisfactory result: NSE_val > NSE_cal - 0.05
# Red flag: NSE_val < NSE_cal - 0.10 → overfitting
```

---

## Reporting Template

```
MODEL PERFORMANCE SUMMARY
─────────────────────────────────────
Period:          YYYY–YYYY
Warm-up:         2 years

CALIBRATION        | VALIDATION
NSE:     X.XX      | X.XX
KGE:     X.XX      | X.XX  
PBIAS:   X.X%      | X.X%
NSE_log: X.XX      | X.XX

FDC assessment: [High flows: ✓/✗  Mid: ✓/✗  Low: ✓/✗]
Seasonal bias: [month with largest error]
─────────────────────────────────────
Verdict: [SATISFACTORY / NEEDS IMPROVEMENT]
Main issue: [one sentence]
```
