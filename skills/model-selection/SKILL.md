---
name: model-selection
description: Guide the selection of the appropriate hydrological model (conceptual vs neural) based on catchment type, data availability, and modelling purpose
when_to_use: When the user asks which model to use, wants to choose between HBV and LSTM, asks for model recommendations, or is unsure how to start rainfall-runoff modelling
domain: modelling
tools_used: []
tags:
  - model-selection
  - HBV
  - LSTM
  - conceptual
  - neural-hydrology
  - decision
---

# Hydrological Model Selection Workflow

## Purpose
Guide the user to the most appropriate modelling approach before any code is written. Wrong model choice is the most expensive mistake in hydrology — fix it at the decision stage.

## When This Workflow Applies
- User asks "which model should I use?"
- User is unsure whether to use HBV, LSTM, or something else
- User wants to model streamflow but hasn't started yet
- User asks about "conceptual vs data-driven" models

---

## Decision Framework

Work through these questions in order:

### Q1: What is the modelling purpose?

| Purpose | Preferred approach |
|---|---|
| Understand process / interpret parameters | **Conceptual (HBV)** |
| Highest accuracy for prediction | **Neural (LSTM)** |
| Ungauged catchment extrapolation | **Conceptual or regional** |
| Real-time forecasting | **LSTM with recent data** |
| Educational / explainable results | **Conceptual** |

### Q2: How much data is available?

| Training record | Suitable models |
|---|---|
| < 5 years | Conceptual only |
| 5–20 years | Conceptual preferred; LSTM with caution |
| > 20 years | Both; LSTM likely better accuracy |
| Multiple gauges (10+) | LSTM with regional training |

### Q3: Is the catchment in CAMELS?

- **Yes → LSTM is viable**: pre-trained regional models exist; attributes are available
- **No → HBV is safer**: LSTM without static attributes loses much of its advantage

---

## Model Profiles

### HBV-Light (Conceptual)

**Strengths:**
- Interpretable parameters (soil moisture, groundwater storage, routing)
- Works well with short records (5+ years)
- Fast to run; easy to calibrate with AI-Hydro
- Parameters have physical meaning → can detect data errors

**Weaknesses:**
- Structural errors for complex catchments (glaciers, karst)
- Cannot learn from spatial heterogeneity implicitly

**Best for:** Understanding catchment behaviour, teaching, process studies, ungauged extrapolation via regionalisation

```
Model: HBV-Light via train_hydro_model(model_type="hbv")
Parameters: FC, LP, BETA, K0, K1, K2, UZL, PERC, MAXBAS
Calibration: NSE + KGE multi-objective
```

---

### LSTM (Neural Hydrology)

**Strengths:**
- Superior accuracy on gauged catchments with long records
- Handles non-linearities and memory effects implicitly
- Can incorporate static attributes (area, climate indices, soil type)
- Transferable across basins when trained regionally

**Weaknesses:**
- Black box — parameters aren't interpretable
- Needs ≥ 10–20 years to train reliably
- Can fail silently on out-of-distribution conditions

**Best for:** Operational forecasting, benchmarking, large multi-basin studies

```
Model: LSTM via train_hydro_model(model_type="lstm")
Inputs: P, T (min/max), PE + static CAMELS attributes
Hidden: 64–256 units; sequence length 365 days recommended
```

---

## Recommended Starting Point by Scenario

### Scenario A: "I have a gauged CAMELS basin, want best accuracy"
→ **LSTM with regional pre-training**
1. `extract_camels_attributes` → get static features
2. `fetch_streamflow_data` + `fetch_forcing_data` (30 years)
3. `train_hydro_model(model_type="lstm", epochs=30, hidden_size=128)`
4. Evaluate on 10-year holdout

### Scenario B: "I want to understand my catchment's behaviour"
→ **HBV-Light**
1. `fetch_streamflow_data` + `fetch_forcing_data`
2. `train_hydro_model(model_type="hbv")`
3. Inspect calibrated parameters → interpret vs catchment characteristics
4. Run sensitivity analysis on BETA (soil moisture nonlinearity)

### Scenario C: "Short record (< 10 years), no CAMELS"
→ **HBV-Light with regionalisation**
1. Train HBV on the available record
2. Compare calibrated parameters to CAMELS catchments with similar climate/geology
3. Use donor catchment parameters as prior / initial guess

### Scenario D: "Ungauged catchment"
→ **Regional LSTM or parameter transfer**
1. Identify 5–10 gauged donor catchments with similar attributes
2. Train LSTM on donors; apply to target (zero-shot)
3. Or: regionalise HBV parameters via regression on catchment attributes

---

## Red Flags — When to Stop and Reassess

- Calibrated HBV NSE < 0.50: suspect data errors (check forcings, area)
- LSTM training loss diverging: check for NaN in inputs, reduce learning rate
- Q_sim >> Q_obs in winter: likely snowmelt routine needed (HBV has it; LSTM needs snow features)
- Negative KGE: model is worse than climatology — start over with data quality check

---

## Suggested First Message After Selection

Once model type is decided, suggest:
> "Shall I run a calibration with [HBV / LSTM] now? I'll need the gauge ID and a date range for calibration (warm-up + train + validation)."
