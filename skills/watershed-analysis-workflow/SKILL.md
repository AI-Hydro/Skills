---
name: watershed-analysis-workflow
description: End-to-end watershed characterisation — delineation, terrain analysis, land cover, soils, hydrological signatures, and CAMELS attributes
when_to_use: When the user wants a complete watershed analysis, catchment characterisation, or asks to "analyse" or "characterise" a gauge or watershed
domain: composition
tools_used:
  - delineate_watershed
  - compute_twi
  - fetch_streamflow_data
  - extract_hydrological_signatures
  - extract_geomorphic_parameters
  - fetch_forcing_data
  - extract_camels_attributes
tags:
  - watershed
  - catchment
  - delineation
  - TWI
  - signatures
  - CAMELS
---

# Watershed Analysis Workflow

## Purpose
Produce a comprehensive characterisation of a catchment from a pour point or gauge ID. Covers terrain, land cover, soils, climate, and hydrological response.

## When This Workflow Applies
- User says "analyse this watershed / catchment"
- User provides coordinates and asks for a full characterisation
- User wants to compare two catchments
- User is preparing inputs for a rainfall-runoff model
- User asks "what does this catchment look like?"

---

## Workflow Overview

```
Pour point / Gauge ID
        │
        ▼
1. Delineate watershed boundary
        │
        ▼
2. Terrain analysis (DEM → TWI, slope, area)
        │
        ▼
3. Fetch streamflow + forcing data
        │
        ▼
4. Extract hydrological signatures
        │
        ▼
5. Pull CAMELS attributes (if CAMELS gauge)
        │
        ▼
6. Synthesise → catchment report
```

---

## Step 1 — Delineate Watershed

```python
# Option A: from gauge ID
watershed = delineate_watershed(gauge_id="XXXXXXXX")

# Option B: from coordinates
watershed = delineate_watershed(lat=40.5, lon=-105.2, area_km2_hint=500)
```

Check output:
- `area_km2` — is it plausible for the gauge record?
- `geometry` — plot and visually confirm it wraps the expected drainage area
- Flag if area differs >20% from USGS published area

---

## Step 2 — Terrain Analysis

```python
twi_result = compute_twi(geometry=watershed["geometry"])
geomorph = extract_geomorphic_parameters(geometry=watershed["geometry"])
```

Key metrics to extract:
| Parameter | Meaning |
|---|---|
| Mean TWI | Wetness tendency; high = wetter soils |
| Mean slope (°) | Controls runoff velocity |
| Relief (m) | High → flashy, low → groundwater-dominated |
| Elongation ratio | Shape: elongated → attenuated peaks |
| Drainage density | High → faster response |

---

## Step 3 — Streamflow and Forcing

```python
# 30+ years recommended for signatures
Q = fetch_streamflow_data(gauge_id="XXXXXXXX", start_date="1990-01-01", end_date="2023-12-31")
forcing = fetch_forcing_data(geometry=watershed["geometry"], start_date="1990-01-01", end_date="2023-12-31")
```

Compute basic water balance:
```python
P = forcing["data"]["precipitation_mm_day"].mean() * 365   # mm/year
ET_approx = forcing["data"]["pet_mm_day"].mean() * 365     # mm/year
Q_mm = (Q["data"]["discharge_m3s"].mean() * 86400 * 365) / (watershed["area_km2"] * 1e6) * 1000
aridity = ET_approx / P
runoff_ratio = Q_mm / P
print(f"P={P:.0f} mm/yr | ET≈{ET_approx:.0f} mm/yr | Q={Q_mm:.0f} mm/yr | RR={runoff_ratio:.2f} | AI={aridity:.2f}")
```

---

## Step 4 — Hydrological Signatures

```python
sigs = extract_hydrological_signatures(gauge_id="XXXXXXXX")
```

Report these key signatures:
| Signature | Value | Interpretation |
|---|---|---|
| BFI | — | Groundwater contribution |
| Q50 / mean Q | — | Flow variability |
| Runoff coefficient | — | Rainfall efficiency |
| FDC slope (Q33/Q66) | — | Regime flashiness |
| Mean annual flood | — | Flood potential |
| Low-flow Q95 | — | Drought indicator |

---

## Step 5 — CAMELS Attributes (if available)

```python
camels = extract_camels_attributes(gauge_id="XXXXXXXX")
```

Compare computed signatures to CAMELS-reported values:
- If they agree within ±10%: data is consistent ✓
- If they disagree: flag possible regulation, diversions, or period differences

---

## Step 6 — Synthesise and Report

Structure the output as a **Catchment Factsheet**:

```
═══════════════════════════════════════════════
CATCHMENT SUMMARY — Gauge XXXXXXXX
═══════════════════════════════════════════════

LOCATION & GEOMETRY
  Drainage area:     XXX km²
  Mean elevation:    XXX m
  Mean slope:        X.X°
  Shape:             [elongated / compact]

CLIMATE (1990–2023)
  Mean annual P:     XXX mm/yr
  Aridity index:     X.XX
  Snow fraction:     XX%

HYDROLOGY
  Mean annual Q:     X.XX m³/s  (XXX mm/yr)
  Runoff ratio:      X.XX
  BFI:               X.XX
  Q₁₀₀:             XX m³/s  (est.)

CATCHMENT CHARACTER
  [1–2 sentence narrative interpretation]
═══════════════════════════════════════════════
```

**Narrative interpretation guidance:**
- Arid (AI > 1.5) + low BFI → ephemeral, event-driven, drought-sensitive
- Humid (AI < 0.5) + high BFI → stable groundwater-fed, reliable low flows
- Steep + high drainage density → flashy, short time-of-concentration
- Flat + high TWI → waterlogging risk, saturation-excess runoff
