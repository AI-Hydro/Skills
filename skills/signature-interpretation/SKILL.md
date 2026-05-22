---
name: signature-interpretation
description: Interpret hydrological signatures extracted from streamflow to characterise catchment behaviour and diagnose anomalies
when_to_use: When the user has extracted signatures and wants to understand what they mean, asks to "interpret" results, or wants to compare a catchment to regional norms
domain: interpretation
tools_used:
  - extract_hydrological_signatures
  - extract_camels_attributes
  - get_session_summary
tags:
  - signatures
  - interpretation
  - FDC
  - BFI
  - seasonality
  - catchment-behaviour
---

# Hydrological Signature Interpretation Workflow

## Purpose
Transform a table of computed hydrological signatures into a coherent narrative about catchment behaviour. Numbers without interpretation are not useful to most users.

## When This Workflow Applies
- `extract_hydrological_signatures` just ran — user wants to understand the output
- User asks "what do these numbers mean?"
- User wants to compare their catchment to CAMELS benchmarks
- User asks for a "summary" or "story" of what the streamflow record shows

---

## Signature Reference Guide

### 1. Baseflow Index (BFI)

| Value | Interpretation |
|---|---|
| > 0.80 | Highly permeable geology (chalk, karst, sandstone); stable, groundwater-fed |
| 0.50–0.80 | Mixed geology; moderate groundwater contribution |
| 0.25–0.50 | Moderately impermeable; seasonal groundwater |
| < 0.25 | Impermeable (clay/granite); flashy, event-driven regime |

**Cross-check:** Compare with soil permeability class and geology. Mismatch → suspect regulation or data error.

---

### 2. Mean Annual Runoff Ratio (Q/P)

| Value | Interpretation |
|---|---|
| > 0.70 | Wet climate, low ET demand (maritime / high elevation) |
| 0.40–0.70 | Temperate, balanced water budget |
| 0.20–0.40 | Semi-arid; ET dominates |
| < 0.20 | Arid; most P lost to ET; streamflow unreliable |

**Budyko check:** Plot (ET/P) vs (PET/P). Points near the Budyko curve → water balance is closed. Points above → possible groundwater input or irrigation; below → water abstraction or storage increase.

---

### 3. Flow Duration Curve Slope (Q₁₀/Q₉₀ ratio)

High values (flashy) → responsive catchment, low storage, impermeable soils
Low values (stable) → high storage, permeable geology, or regulated flow

| Q₁₀/Q₉₀ | Regime type |
|---|---|
| > 100 | Extremely flashy (arid / urban) |
| 20–100 | Flashy (impermeable / steep) |
| 5–20 | Mixed |
| 1–5 | Stable (permeable / regulated) |

---

### 4. Mean Annual Flood (Q_mean_annual) and Q₁₀₀/Q_mean

The ratio of 100-year flood to mean annual flood measures **flood amplification**:
- Low ratio (3–5) → stable, groundwater-dominated catchments
- High ratio (10–30) → flashy, semi-arid catchments where rare floods are extreme multiples of mean flow

---

### 5. Seasonality Index (SI)

Measures whether flow is concentrated in a season:
- SI ≈ 0 → perennial, evenly distributed flow (groundwater-fed)
- SI → 1 → strong seasonal concentration (snowmelt, monsoon)

```python
# Compute SI from monthly means
monthly_Q = Q.resample('ME').mean()
annual_mean = monthly_Q.mean()
SI = (1 / annual_mean) * np.sum(np.abs(monthly_Q - annual_mean)) / 12
```

---

### 6. Rising and Falling Limb Densities

- **High rising limb density (RLD)** → rapid storm response, low initial abstraction
- **High falling limb density (FLD)** → fast recession, low storage

Both high → flashy catchment.
Both low → dampened, storage-dominated.

---

## Interpretation Workflow

```python
sigs = extract_hydrological_signatures(gauge_id="XXXXXXXX")
camels = extract_camels_attributes(gauge_id="XXXXXXXX")  # for comparison
```

### Step 1 — Screen for Data Quality Flags

Before interpreting, check:
- `missing_data_fraction` > 0.05 → flag; signatures may be unreliable
- `regulated` flag → interpret with caution; BFI especially affected
- Record length < 15 years → note uncertainty on all signatures

### Step 2 — Build the Catchment Narrative

Use this template:

```
CATCHMENT CHARACTER NARRATIVE
─────────────────────────────────────────
[Gauge ID] is a [REGIME TYPE] catchment based on:

WATER BALANCE
  Runoff ratio: [value] → [interpretation]
  Aridity index: [value] → [humid/semi-arid/arid]

FLOW REGIME
  BFI: [value] → [permeable/mixed/impermeable]
  FDC slope (Q10/Q90): [value] → [flashy/stable]
  Seasonality: [SI value] → [seasonal/perennial]

FLOOD BEHAVIOUR  
  Mean annual flood: [value] m³/s
  Q100/Qmean ratio: [value] → [moderate/extreme amplification]

COMPARED TO CAMELS PEERS
  [Is BFI above/below median for similar climate class?]
  [Is runoff ratio consistent with aridity index?]

SUMMARY
  In one paragraph: integrate all signals into a coherent story.
  Identify the dominant controls (geology, climate, topography).
  Flag any anomalies and their likely cause.
─────────────────────────────────────────
```

### Step 3 — Flag Anomalies

These signature combinations suggest problems worth investigating:

| Anomaly | Possible cause |
|---|---|
| High BFI + low runoff ratio | Possible deep groundwater loss or abstraction |
| Q/P > 1.0 | Snowmelt contribution, interbasin transfer, or area error |
| Seasonality opposite to climate | Check gauge location — may be on a regulated river |
| NSE_log >> NSE | Model handles low flows well but misses peaks → check storm routing |
| RR very different from CAMELS neighbour | Regulation, land use change, or period difference |

### Step 4 — Comparative Context

Always situate the catchment relative to regional norms:

```python
# Compare to CAMELS catchments in similar climate class
similar = camels[camels['aridity'].between(aridity * 0.8, aridity * 1.2)]
print(f"BFI: this={bfi:.2f}  | CAMELS median={similar['baseflow_index'].median():.2f}")
print(f"RR:  this={rr:.2f}   | CAMELS median={similar['runoff_ratio'].median():.2f}")
```

A catchment that is unusual within its climate class is interesting — worth explaining why.
