---
name: flood-frequency-analysis
description: Fit flood frequency distributions and compute return-period quantiles from annual maximum series
when_to_use: When the user asks about return periods, T-year floods, frequency analysis, flood quantiles, GEV fitting, LP3, or designing for a specific AEP
domain: frequency-analysis
tools_used:
  - fetch_streamflow_data
  - extract_hydrological_signatures
tags:
  - flood
  - frequency
  - return-period
  - GEV
  - LP3
  - AEP
---

# Flood Frequency Analysis Workflow

## Purpose
Estimate flood magnitudes for specified return periods (e.g. 2-, 10-, 100-year) by fitting a frequency distribution to the annual maximum series (AMS) at a stream gauge.

## When This Workflow Applies
- User asks for "the 100-year flood" or "T-year return period"
- User wants to size a culvert, dam spillway, or floodplain map
- User asks about Annual Exceedance Probability (AEP)
- User wants to compare flood frequency curves across gauges

---

## Step 1 — Fetch the Annual Maximum Series

Use `fetch_streamflow_data` to retrieve daily streamflow, then extract the AMS:

```python
# Recommended: at least 20 years of record for reliable estimates
# Prefer gauges with < 10% missing data
result = fetch_streamflow_data(gauge_id="XXXXXXXX", start_date="1980-01-01", end_date="2023-12-31")
ams = result["data"].resample("YE").max()
```

**Check first:**
- Record length ≥ 20 years (30+ preferred)
- No major regulation changes mid-record (dams, diversions)
- Flag years with > 30 days missing as potentially unreliable

---

## Step 2 — Screen the Data

Before fitting, always:
1. Plot the AMS as a time series — look for trends (climate non-stationarity)
2. Check for outliers using Grubbs-Beck test (high and low outliers)
3. Note if regulation or land-use change breaks the record

**If a trend is detected:** warn the user that stationary frequency analysis may underestimate future risk.

---

## Step 3 — Fit Distributions

Fit at least two distributions and compare:

| Distribution | Recommended for |
|---|---|
| **GEV** (Generalized Extreme Value) | Most gauges; flexible shape parameter |
| **LP3** (Log-Pearson Type III) | US Federal standard (Bulletin 17C) |
| **Gumbel** (EV1) | When shape ≈ 0; simpler |

```python
import numpy as np
from scipy import stats

log_ams = np.log(ams.dropna())

# LP3: fit Pearson III to log-transformed data
shape, loc, scale = stats.pearson3.fit(log_ams)

# Return period quantiles
return_periods = [2, 5, 10, 25, 50, 100, 200, 500]
aep = [1/T for T in return_periods]
quantiles_lp3 = np.exp(stats.pearson3.ppf([1-p for p in aep], shape, loc, scale))

# GEV: fit directly to AMS
c, loc_gev, scale_gev = stats.genextreme.fit(ams.dropna())
quantiles_gev = stats.genextreme.ppf([1-p for p in aep], c, loc_gev, scale_gev)
```

---

## Step 4 — Compute Confidence Intervals

Bootstrap 95% CIs to communicate uncertainty:

```python
n_boot = 1000
boot_quantiles = np.zeros((n_boot, len(return_periods)))
ams_clean = ams.dropna().values

for i in range(n_boot):
    sample = np.random.choice(ams_clean, size=len(ams_clean), replace=True)
    log_s = np.log(sample)
    sh, lo, sc = stats.pearson3.fit(log_s)
    boot_quantiles[i] = np.exp(stats.pearson3.ppf([1-p for p in aep], sh, lo, sc))

ci_lower = np.percentile(boot_quantiles, 2.5, axis=0)
ci_upper = np.percentile(boot_quantiles, 97.5, axis=0)
```

---

## Step 5 — Present Results

Always present:
1. **Frequency curve plot** — log-scale x-axis (return period), y-axis (discharge)
   - Plot empirical points using Weibull plotting position: `rank / (n+1)`
   - Overlay fitted LP3 and GEV curves
   - Show 95% CI as a shaded band
2. **Results table** — Q₂, Q₁₀, Q₁₀₀, Q₅₀₀ with CIs
3. **Goodness-of-fit** — report AIC/BIC for each distribution

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 6))
ax.semilogx(return_periods, quantiles_lp3, 'b-', label='LP3', linewidth=2)
ax.semilogx(return_periods, quantiles_gev, 'r--', label='GEV', linewidth=2)
ax.fill_between(return_periods, ci_lower, ci_upper, alpha=0.2, label='LP3 95% CI')
# Add empirical points
n = len(ams_clean)
plotting_pos = np.sort(ams_clean)
emp_rp = (n + 1) / np.arange(n, 0, -1)
ax.scatter(emp_rp, plotting_pos, color='k', zorder=5, label='Observed AMS')
ax.set_xlabel('Return Period (years)')
ax.set_ylabel('Peak Discharge (m³/s)')
ax.legend()
ax.grid(True, which='both', alpha=0.3)
plt.tight_layout()
```

---

## Step 6 — Interpretation Guidance

Tell the user:
- **Q₁₀₀ = X m³/s** means there is a 1% chance of this flow being exceeded in any given year
- Confidence intervals widen at longer return periods — acknowledge this
- Short records (< 30 years) produce wide CIs; Q₅₀₀ from 20 years of data is highly uncertain
- Recommend regional frequency analysis or index-flood methods if record < 15 years

---

## Common Pitfalls to Flag

| Issue | Action |
|---|---|
| Regulated flow | Warn user; suggest naturalized flow or USGS regulated-record methods |
| Negative shape (heavy tail GEV) | Highlight — implies unbounded upper tail |
| LP3 vs GEV disagree >20% at Q₁₀₀ | Report both; recommend sensitivity analysis |
| Record < 20 years | Strongly recommend regional pooling |
