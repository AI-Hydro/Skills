---
name: interactive-module-builder
description: Create production-grade AI-Hydro interactive learning modules — self-contained HTML files with executable Python cells, sliders, quizzes, scrollytelling, real AI-Hydro branding (animated gradient droplet logo, dark theme, cyan accent, Poppins/Nunito/Quicksand fonts), peer-reviewed citations, full provenance footer, and CC-BY-4.0 license. Modules open automatically in AI-Hydro's built-in HTML Preview panel (which supports Python/JS cell execution); do NOT assume an external browser. Use when the user asks to create a learning module, tutorial, interactive lesson, educational artifact, or "explain X with visuals" for any hydrology topic.
when_to_use: When the user asks to create a learning module, tutorial, interactive lesson, educational content, "explain X with visuals", "make a module about", "create a tutorial for", or "build an interactive lesson on" any hydrology topic.
domain: general
tools_used:
  - show_html_preview
  - get_researcher_profile
tags:
  - learning-module
  - interactive
  - html-artifact
  - education
  - tutorial
  - production-grade
---

# AI-Hydro Interactive Module Builder

Create **production-grade** self-contained HTML learning modules that:
- Render automatically in AI-Hydro's built-in HTML Preview panel (cells execute via the bundled Python kernel — no external browser needed)
- Look unmistakably AI-Hydro on first frame (real gradient-droplet logo with breathing animation, dark theme, cyan accent, Poppins/Nunito/Quicksand fonts)
- Are scientifically credible (peer-reviewed citations, complete provenance, named authors, license)
- Degrade gracefully when opened in a plain browser (static content renders; Run buttons show "Open in AI-Hydro to run")

## When This Skill Applies

- User asks to create a learning module, tutorial, or interactive lesson
- User wants to "explain X with visuals" for a hydrology concept
- User wants an interactive educational artifact
- User asks to build something for teaching hydrology

---

# THE STANDARDIZATION CONTRACT

Every module MUST contain these 8 sections, in this order. **If any is missing, the module fails the production-grade contract.**

| # | Section | Required content |
|---|---|---|
| 1 | Manifest block | `<script type="application/vnd.aihydro.module+json">` in `<head>` with all fields populated |
| 2 | Branded hero | Real AI-Hydro gradient droplet SVG (animated pulse), title in Poppins, author byline, license + estimated-time pills |
| 3 | Workflow strip | 5–7 step horizontal navigation with anchor links |
| 4 | Content sections | Prose + interactive JS + executable `.aihydro-cell` + callouts + at least one quiz checkpoint |
| 5 | Provenance footer | Methods, Data, Software, Generated date, Reproducibility |
| 6 | References | At least one peer-reviewed citation per non-trivial method (use the library below) |
| 7 | License badge | Visible CC-BY-4.0 pill linking to https://creativecommons.org/licenses/by/4.0/ |
| 8 | "Made with AI-Hydro" banner | Small footer tag with link to https://github.com/AI-Hydro/AI-Hydro |

---

# CELL FORMAT — Use These Class Names Exactly

The AI-Hydro HTML Preview kernel discovers and executes cells by querying the DOM. The class names, attributes, and structure below are **the contract** between your module and the bundled kernel. Anything else will not execute.

## Executable Python cell — canonical structure

```html
<div class="aihydro-cell" data-aihydro-cell-id="bfi-filter" data-language="python">
  <div class="aihydro-cell-header">
    <span class="aihydro-cell-lang">python</span>
    <span class="aihydro-cell-desc">Lyne–Hollick recursive digital filter on a synthetic hydrograph</span>
    <button class="aihydro-run" type="button">Run ▶</button>
  </div>
  <pre class="aihydro-source">import numpy as np
import matplotlib.pyplot as plt

# Synthetic hydrograph
t = np.arange(365)
Q = 5 + 20 * np.exp(-((t - 90) ** 2) / 200) + np.random.lognormal(0.5, 0.4, 365)

# Lyne-Hollick one-pass recursive filter
alpha = 0.925
bf = np.zeros_like(Q)
bf[0] = Q[0]
for i in range(1, len(Q)):
    bf[i] = alpha * bf[i-1] + 0.5 * (1 - alpha) * (Q[i] + Q[i-1])
    bf[i] = min(bf[i], Q[i])

bfi = bf.sum() / Q.sum()

fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(t, Q,  color="#00A3FF", lw=0.9, label="Streamflow")
ax.plot(t, bf, color="#00DDFF", lw=0.8, ls="--", label=f"Baseflow (BFI={bfi:.3f})")
ax.fill_between(t, 0, bf, color="#00DDFF", alpha=0.12)
ax.set_xlabel("Day of year"); ax.set_ylabel("Q (m³/s)")
ax.legend(); plt.tight_layout(); plt.show()
</pre>
  <div class="aihydro-output" aria-live="polite"></div>
</div>
```

### Cell format MUST-DOs and MUST-NOTs

| ✅ MUST | ❌ MUST NOT |
|---|---|
| `<div class="aihydro-cell" data-aihydro-cell-id="UNIQUE_ID" data-language="python">` | `data-lang="..."` or missing `data-aihydro-cell-id` |
| `<button class="aihydro-run" type="button">Run ▶</button>` (no onclick) | `<button class="aihydro-run-cell" onclick="runPythonCell(this)">` |
| `<pre class="aihydro-source">…code…</pre>` (no `<code>` wrapper) | `<pre><code>…code…</code></pre>` |
| `<div class="aihydro-output" aria-live="polite"></div>` (sibling of the `<pre>`) | `<div class="aihydro-output" id="some-id">` (id collisions break multiple cells) |
| `data-aihydro-cell-id` unique within the module | duplicate IDs (kernel uses first match only) |

The kernel auto-injects a stylesheet with `.aihydro-*` classes; your module's CSS should only override branding tokens (`--aihydro-blue`, etc.), not redefine the cell visuals.

---

# AI-HYDRO BRANDING PACK (use ALL of these)

## Real AI-Hydro logo — inline SVG

Embed the gradient droplet logo at the top of every module (not the emoji 💧, not a placeholder). This is the same artwork used in the VS Code extension icon:

```html
<svg class="aihydro-hero-logo" width="96" height="96" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="aihydroDropletGrad" x1="50" y1="10" x2="50" y2="90" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#00A3FF"/>
      <stop offset="100%" stop-color="#00DDFF"/>
    </linearGradient>
  </defs>
  <path d="M50 10 C50 10 25 35 25 55 C25 70 35 85 50 85 C65 85 75 70 75 55 C75 35 50 10 50 10 Z"
        fill="url(#aihydroDropletGrad)"/>
  <ellipse cx="20" cy="52" rx="5" ry="7" fill="url(#aihydroDropletGrad)"/>
  <ellipse cx="80" cy="52" rx="5" ry="7" fill="url(#aihydroDropletGrad)"/>
  <ellipse cx="40" cy="48" rx="6" ry="9" fill="#1a1a2e"/>
  <ellipse cx="60" cy="48" rx="6" ry="9" fill="#1a1a2e"/>
  <path d="M 38 62 Q 50 68 62 62" stroke="#1a1a2e" stroke-width="3" fill="none" stroke-linecap="round"/>
  <circle cx="50" cy="14" r="4" fill="url(#aihydroDropletGrad)"/>
</svg>
```

For the footer "Made with AI-Hydro" tag, reuse the same SVG at `width="20" height="20"`.

## Breathing pulse animation (mandatory)

```css
@keyframes aihydro-pulse {
  0%, 100% { transform: scale(1);    filter: drop-shadow(0 0 8px rgba(0,163,255,0.40)); }
  50%      { transform: scale(1.04); filter: drop-shadow(0 0 14px rgba(0,221,255,0.65)); }
}
.aihydro-hero-logo { animation: aihydro-pulse 3s ease-in-out infinite; }
@media (prefers-reduced-motion: reduce) {
  .aihydro-hero-logo { animation: none; }
}
```

No spinning, no rainbow, no neon glare. Respect `prefers-reduced-motion` (mandatory).

## Typography (Google Fonts — load in `<head>`)

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Quicksand:wght@500;700&family=Poppins:wght@500;600;700&family=Nunito:wght@400;700&family=JetBrains+Mono:wght@400;600&display=swap">
```

| Role | Font | Weight |
|---|---|---|
| Hero / wordmark | Quicksand | 700 |
| Headings (h1-h3) | Poppins | 600 / 500 |
| Body text | Nunito | 400 / 700 |
| Code | JetBrains Mono | 400 |

## Color palette — ONLY these tokens

```css
:root {
  --aihydro-blue:       #00A3FF;
  --aihydro-cyan:       #00DDFF;
  --aihydro-bg-deep:    #0a0a15;
  --aihydro-bg-navy:    #1a1a2e;
  --aihydro-bg-mid:     #0f0f1e;
  --aihydro-text:       #FFFFFF;
  --aihydro-text-accent:#7dd3fc;
  --aihydro-text-muted: #94a3b8;
  --aihydro-warn:       #fbbf24;     /* for warnings only */
  --aihydro-success:    #34d399;     /* for success states only */
}
```

**Forbidden:** red, orange, generic yellow, white backgrounds by default, fonts not on the list above. (Warm `#fbbf24` is allowed only in warning callouts.)

---

# BUILT-IN CITATION LIBRARY

When a module covers a method below, you **must** cite the canonical reference. Do not invent citations.

| Topic | Citation |
|---|---|
| Baseflow separation (recursive digital filter) | Lyne, V., Hollick, M. (1979). Stochastic time-variable rainfall-runoff modelling. *Hydrology and Water Resources Symposium*, 89–93. |
| Eckhardt baseflow filter | Eckhardt, K. (2005). How to construct recursive digital filters for baseflow separation. *Hydrol. Proc.* 19, 507–515. |
| Flood frequency (Bulletin 17C) | Cohn, T.A., England, J.F., Berenbrock, C.E., Mason, R.R., Stedinger, J.R., Lamontagne, J.R. (2013). A generalized Grubbs–Beck test statistic for detecting multiple potentially influential low outliers in flood series. *Water Resour. Res.* 49(8), 5047–5058. |
| Topographic Wetness Index (TWI) | Beven, K.J., Kirkby, M.J. (1979). A physically based, variable contributing area model of basin hydrology. *Hydrological Sciences Bulletin* 24(1), 43–69. |
| Hydrological signatures | Westerberg, I.K., McMillan, H.K. (2015). Uncertainty in hydrological signatures. *HESS* 19, 3951–3968. |
| Budyko framework | Budyko, M.I. (1974). *Climate and Life.* Academic Press. Fu, B. (1981). On the calculation of the evaporation from land surface. *Sci. Atmos. Sin.* 5, 23–31. |
| NSE | Nash, J.E., Sutcliffe, J.V. (1970). River flow forecasting through conceptual models. *J. Hydrol.* 10(3), 282–290. |
| KGE | Gupta, H.V., Kling, H., Yilmaz, K.K., Martinez, G.F. (2009). Decomposition of the mean squared error and NSE performance criteria. *J. Hydrol.* 377, 80–91. |
| HBV model | Bergström, S. (1976). Development and application of a conceptual runoff model for Scandinavian catchments. SMHI Report RHO 7. Seibert, J., Vis, M.J.P. (2012). Teaching hydrological modeling with a user-friendly catchment-runoff-model software package. *HESS* 16, 3315–3325. |
| CAMELS dataset (US) | Newman, A.J. et al. (2015). Development of a large-sample watershed-scale hydrometeorological data set for the contiguous USA. *HESS* 19, 209–223. Addor, N. et al. (2017). The CAMELS data set. *HESS* 21, 5293–5313. |
| Watershed delineation (D8) | O'Callaghan, J.F., Mark, D.M. (1984). The extraction of drainage networks from digital elevation data. *Computer Vision, Graphics, and Image Processing* 28(3), 323–344. |
| Curve Number | NRCS (2004). *National Engineering Handbook, Part 630: Hydrology, Chapter 10: Estimation of Direct Runoff from Storm Rainfall.* USDA. |

If your topic is not listed, search the literature and add the most-cited canonical paper. Never fabricate a citation.

---

# THE CANONICAL MODULE SKELETON (copy this verbatim, swap content)

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{{TITLE}} — AI-Hydro Module</title>
<meta name="viewport" content="width=device-width, initial-scale=1">

<!-- Module manifest — the marketplace + preview panel parse this -->
<script type="application/vnd.aihydro.module+json">
{
  "id": "{{SLUG}}",
  "title": "{{TITLE}}",
  "version": "0.1.0",
  "authors": [
    { "name": "AI-Hydro Agent", "affiliation": "AI-Hydro Platform", "orcid": null }
  ],
  "license": "CC-BY-4.0",
  "topic": "{{TOPIC}}",
  "level": "intro",
  "estimated_minutes": 15,
  "requires": { "executable": true, "python": ["numpy", "matplotlib"] },
  "citation": { "text": "AI-Hydro (2026). {{TITLE}}. AI-Hydro Modules.", "doi": null },
  "created_at": "{{YYYY-MM-DD}}",
  "ai_hydro_preview_min_version": "0.1.24"
}
</script>

<!-- Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Quicksand:wght@500;700&family=Poppins:wght@500;600;700&family=Nunito:wght@400;700&family=JetBrains+Mono:wght@400;600&display=swap">

<style>
:root {
  --aihydro-blue: #00A3FF;
  --aihydro-cyan: #00DDFF;
  --aihydro-bg-deep: #0a0a15;
  --aihydro-bg-navy: #1a1a2e;
  --aihydro-bg-mid: #0f0f1e;
  --aihydro-text: #FFFFFF;
  --aihydro-text-accent: #7dd3fc;
  --aihydro-text-muted: #94a3b8;
  --aihydro-warn: #fbbf24;
}

body.aihydro-module {
  margin: 0; padding: 32px 24px;
  max-width: 980px; margin-inline: auto;
  background: linear-gradient(180deg, var(--aihydro-bg-deep) 0%, var(--aihydro-bg-navy) 100%);
  color: var(--aihydro-text-accent);
  font-family: 'Nunito', system-ui, sans-serif;
  line-height: 1.7;
  min-height: 100vh;
}

/* Hero */
.aihydro-hero {
  display: flex; align-items: center; gap: 18px;
  padding: 18px 0 22px;
  border-bottom: 1px solid rgba(125,211,252,0.18);
  margin-bottom: 28px;
}
.aihydro-hero-title { display: flex; flex-direction: column; gap: 4px; }
.aihydro-hero-title h1 {
  margin: 0;
  font-family: 'Quicksand', system-ui, sans-serif;
  font-weight: 700; font-size: 28px;
  background: linear-gradient(135deg, #00D4FF 0%, #00FFFF 100%);
  -webkit-background-clip: text; background-clip: text;
  color: transparent;
}
.aihydro-hero-byline {
  font-family: 'Comfortaa', 'Quicksand', system-ui, sans-serif;
  font-size: 12px; color: var(--aihydro-text-muted);
  display: flex; gap: 10px; flex-wrap: wrap;
}
.aihydro-pill {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 2px 10px; border-radius: 999px;
  border: 1px solid rgba(125,211,252,0.18);
  color: var(--aihydro-text-accent);
  background: rgba(0,221,255,0.06);
  font-size: 11px;
}

@keyframes aihydro-pulse {
  0%, 100% { transform: scale(1);    filter: drop-shadow(0 0 8px rgba(0,163,255,0.40)); }
  50%      { transform: scale(1.04); filter: drop-shadow(0 0 14px rgba(0,221,255,0.65)); }
}
.aihydro-hero-logo { animation: aihydro-pulse 3s ease-in-out infinite; }
@media (prefers-reduced-motion: reduce) { .aihydro-hero-logo { animation: none; } }

/* Workflow strip */
.aihydro-strip {
  display: flex; gap: 10px; overflow-x: auto;
  padding: 14px 0; margin-bottom: 28px;
  border-bottom: 1px solid rgba(125,211,252,0.10);
}
.aihydro-strip a {
  flex: 0 0 auto;
  padding: 8px 14px; border-radius: 999px;
  background: var(--aihydro-bg-mid);
  border: 1px solid rgba(125,211,252,0.18);
  color: var(--aihydro-text-accent);
  font-family: 'Comfortaa', system-ui, sans-serif;
  font-size: 12px; text-decoration: none;
  transition: all .15s ease;
}
.aihydro-strip a:hover {
  border-color: var(--aihydro-cyan);
  box-shadow: 0 0 0 1px var(--aihydro-cyan);
}

/* Section headings */
h2 { font-family: 'Poppins', system-ui, sans-serif; color: var(--aihydro-text); margin-top: 36px; }
h3 { font-family: 'Poppins', system-ui, sans-serif; color: var(--aihydro-text); }

/* Callouts */
.callout {
  border-left: 3px solid var(--aihydro-cyan);
  background: rgba(125,211,252,0.05);
  padding: 12px 16px; margin: 18px 0; border-radius: 6px;
}
.callout.tip     { border-left-color: #34d399; background: rgba(52,211,153,0.07); }
.callout.warning { border-left-color: var(--aihydro-warn); background: rgba(251,191,36,0.07); }
.callout.agent {
  border-left-color: var(--aihydro-blue);
  background: linear-gradient(90deg, rgba(0,163,255,0.10), rgba(0,221,255,0.04));
}

/* Provenance footer */
.aihydro-provenance {
  margin-top: 48px; padding-top: 24px;
  border-top: 1px solid rgba(125,211,252,0.18);
  font-size: 13px;
}
.aihydro-provenance dl { display: grid; grid-template-columns: 140px 1fr; gap: 6px 18px; }
.aihydro-provenance dt {
  font-family: 'Comfortaa', system-ui, sans-serif;
  color: var(--aihydro-text-muted); text-transform: uppercase;
  font-size: 10px; letter-spacing: 0.06em;
}
.aihydro-provenance dd { margin: 0; color: var(--aihydro-text-accent); }
.aihydro-refs { margin-top: 28px; font-size: 13px; }
.aihydro-refs h3 { margin-bottom: 8px; }
.aihydro-refs ol { padding-left: 22px; color: var(--aihydro-text-accent); }

/* Made with AI-Hydro banner */
.aihydro-made-with {
  margin-top: 32px; padding-top: 18px;
  border-top: 1px solid rgba(125,211,252,0.10);
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px; font-size: 11px; color: var(--aihydro-text-muted);
  font-family: 'Comfortaa', system-ui, sans-serif;
}
.aihydro-made-with a { color: var(--aihydro-text-accent); text-decoration: none; }
.aihydro-made-with .aihydro-mini-logo { display: inline-flex; align-items: center; gap: 6px; }
</style>
</head>

<body class="aihydro-module">

<!-- ① HERO -->
<header class="aihydro-hero">
  <svg class="aihydro-hero-logo" width="64" height="64" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="aihydroDropletGrad" x1="50" y1="10" x2="50" y2="90" gradientUnits="userSpaceOnUse">
        <stop offset="0%" stop-color="#00A3FF"/><stop offset="100%" stop-color="#00DDFF"/>
      </linearGradient>
    </defs>
    <path d="M50 10 C50 10 25 35 25 55 C25 70 35 85 50 85 C65 85 75 70 75 55 C75 35 50 10 50 10 Z" fill="url(#aihydroDropletGrad)"/>
    <ellipse cx="20" cy="52" rx="5" ry="7" fill="url(#aihydroDropletGrad)"/>
    <ellipse cx="80" cy="52" rx="5" ry="7" fill="url(#aihydroDropletGrad)"/>
    <ellipse cx="40" cy="48" rx="6" ry="9" fill="#1a1a2e"/>
    <ellipse cx="60" cy="48" rx="6" ry="9" fill="#1a1a2e"/>
    <path d="M 38 62 Q 50 68 62 62" stroke="#1a1a2e" stroke-width="3" fill="none" stroke-linecap="round"/>
    <circle cx="50" cy="14" r="4" fill="url(#aihydroDropletGrad)"/>
  </svg>
  <div class="aihydro-hero-title">
    <h1>{{TITLE}}</h1>
    <div class="aihydro-hero-byline">
      <span>by AI-Hydro Agent</span>
      <span class="aihydro-pill">CC-BY-4.0</span>
      <span class="aihydro-pill">⏱ 15 min</span>
      <span class="aihydro-pill">intro</span>
    </div>
  </div>
</header>

<!-- ② WORKFLOW STRIP -->
<nav class="aihydro-strip" aria-label="Module sections">
  <a href="#sec-1">1 · Introduction</a>
  <a href="#sec-2">2 · Concept</a>
  <a href="#sec-3">3 · Interactive</a>
  <a href="#sec-4">4 · Real data</a>
  <a href="#sec-5">5 · Checkpoint</a>
  <a href="#sec-6">6 · Summary</a>
</nav>

<!-- ③ CONTENT SECTIONS -->
<section id="sec-1">
  <h2>1 · Introduction</h2>
  <p>{{Brief problem framing — why this matters for hydrology.}}</p>
  <div class="callout tip"><strong>Tip:</strong> {{One actionable insight.}}</div>
</section>

<section id="sec-2">
  <h2>2 · Core concept</h2>
  <p>{{Explanation with an interactive JS visualization.}}</p>
  <!-- Optional: SVG / canvas / parameter slider -->
</section>

<section id="sec-3">
  <h2>3 · Try it</h2>
  <p>Adjust the parameters and re-run the cell:</p>

  <div class="aihydro-cell" data-aihydro-cell-id="demo-cell" data-language="python">
    <div class="aihydro-cell-header">
      <span class="aihydro-cell-lang">python</span>
      <span class="aihydro-cell-desc">{{Short description}}</span>
      <button class="aihydro-run" type="button">Run ▶</button>
    </div>
    <pre class="aihydro-source">import numpy as np
import matplotlib.pyplot as plt
# ... synthetic computation here ...
plt.plot(np.arange(100), np.random.randn(100).cumsum(), color="#00A3FF")
plt.show()
</pre>
    <div class="aihydro-output" aria-live="polite"></div>
  </div>
</section>

<section id="sec-4">
  <h2>4 · Real data</h2>
  <p>The same idea applied to {{a real CAMELS gauge or USGS station}}:</p>
  <div class="aihydro-cell" data-aihydro-cell-id="real-data-cell" data-language="python">
    <div class="aihydro-cell-header">
      <span class="aihydro-cell-lang">python</span>
      <span class="aihydro-cell-desc">{{Real-data analysis}}</span>
      <button class="aihydro-run" type="button">Run ▶</button>
    </div>
    <pre class="aihydro-source"># Real-data Python — fetches via dataretrieval or pandas
# Include a tiny embedded CSV fallback so the cell works offline.
</pre>
    <div class="aihydro-output" aria-live="polite"></div>
  </div>
  <div class="callout agent">
    <strong>Try it on your gauge:</strong> Ask the AI-Hydro agent to run this analysis on your own USGS gauge ID.
  </div>
</section>

<section id="sec-5">
  <h2>5 · Checkpoint</h2>
  <p><strong>Q:</strong> {{Conceptual question that tests understanding, not memorization.}}</p>
  <!-- Use the kernel's quiz component:
       <div class="aihydro-question" data-aihydro-answer="2"> ... </div>
       Or render a simple radio set. -->
</section>

<section id="sec-6">
  <h2>6 · Summary</h2>
  <ul>
    <li>{{Key takeaway 1}}</li>
    <li>{{Key takeaway 2}}</li>
    <li>{{Key takeaway 3}}</li>
  </ul>
</section>

<!-- ⑤ PROVENANCE FOOTER -->
<footer class="aihydro-provenance">
  <h3 style="margin-top:0; font-family:'Poppins',sans-serif; color:var(--aihydro-text);">Provenance</h3>
  <dl>
    <dt>Methods</dt>     <dd>{{e.g. Lyne–Hollick (1979) recursive digital filter for baseflow separation}}</dd>
    <dt>Data</dt>        <dd>{{e.g. USGS NWIS via the dataretrieval Python package, accessed YYYY-MM-DD}}</dd>
    <dt>Software</dt>    <dd>AI-Hydro v0.1.24, Python 3.11, NumPy, Matplotlib</dd>
    <dt>Generated</dt>   <dd id="aihydro-gen-date">—</dd>
    <dt>Reproducibility</dt><dd>Run all cells top-to-bottom in the AI-Hydro HTML Preview panel.</dd>
  </dl>

  <!-- ⑥ REFERENCES -->
  <section class="aihydro-refs">
    <h3>References</h3>
    <ol>
      <li>{{Primary peer-reviewed citation in full APA/journal form}}</li>
      <li>{{Secondary citation if applicable}}</li>
    </ol>
  </section>

  <!-- ⑦ + ⑧ LICENSE + "Made with AI-Hydro" -->
  <div class="aihydro-made-with">
    <span class="aihydro-mini-logo">
      <svg width="20" height="20" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <defs><linearGradient id="aihydroMiniGrad" x1="50" y1="10" x2="50" y2="90" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#00A3FF"/><stop offset="100%" stop-color="#00DDFF"/></linearGradient></defs>
        <path d="M50 10 C50 10 25 35 25 55 C25 70 35 85 50 85 C65 85 75 70 75 55 C75 35 50 10 50 10 Z" fill="url(#aihydroMiniGrad)"/>
      </svg>
      Made with <a href="https://github.com/AI-Hydro/AI-Hydro" target="_blank" rel="noopener">AI-Hydro</a>
    </span>
    <span><a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC-BY-4.0</a></span>
  </div>
</footer>

<script>
  // Auto-populate generated date
  (function(){
    var el = document.getElementById('aihydro-gen-date');
    if (el) el.textContent = new Date().toISOString().split('T')[0];
  })();

  // Standalone-browser fallback: outside the AI-Hydro preview, disable Run buttons
  (function(){
    var inPreview = (window.AIHYDRO_HTML_PREVIEW_STANDALONE === true) ||
                    (typeof window.aihydro !== 'undefined') ||
                    (typeof window.acquireVsCodeApi === 'function');
    if (inPreview) return;
    document.querySelectorAll('.aihydro-run').forEach(function(btn){
      btn.disabled = true;
      btn.innerHTML = '🔒 Open in AI-Hydro to run';
      btn.style.opacity = '0.55';
      btn.style.cursor = 'not-allowed';
    });
  })();
</script>
</body>
</html>
```

---

# AFTER YOU SAVE THE MODULE

1. Save the HTML file (use the `write_to_file` tool) to the researcher's workspace, e.g. `<workspace>/modules/<slug>.html`.
2. Call `show_html_preview(file_path=...)` so the module opens automatically in the AI-Hydro HTML Preview panel (this is the built-in panel with Python cell execution; do not assume an external browser).
3. In your reply, surface the absolute path to the user and the topics covered.

> **NOTE:** If the user has set a researcher profile (via `get_researcher_profile`), add them as `authors[1]` in the manifest and on the hero byline so the module credits them appropriately.

---

# PRE-PUBLISH CHECKLIST (run before saving)

- [ ] `<script type="application/vnd.aihydro.module+json">` manifest present with ALL fields populated
- [ ] Authors include AI-Hydro Agent (and researcher profile if available)
- [ ] Real AI-Hydro gradient droplet SVG embedded in hero AND in "Made with AI-Hydro" footer
- [ ] Hero animation includes `prefers-reduced-motion` override
- [ ] Quicksand / Poppins / Nunito / JetBrains Mono loaded from Google Fonts
- [ ] Every `.aihydro-cell` has `data-aihydro-cell-id` (unique) + `data-language`
- [ ] Every cell uses `<pre class="aihydro-source">` (NO `<code>` wrapper)
- [ ] Every cell's Run button is `<button class="aihydro-run" type="button">` (NO `onclick`)
- [ ] Workflow strip present at top, 5–7 sections, anchors match `id="sec-N"`
- [ ] At least one quiz checkpoint
- [ ] Provenance footer: Methods, Data, Software, Generated date, Reproducibility — all five rows
- [ ] References section with at least one peer-reviewed citation from the library above
- [ ] CC-BY-4.0 license pill visible in hero AND in footer
- [ ] "Made with AI-Hydro" banner with mini-logo SVG
- [ ] Only branded palette tokens used (no red, no orange, no white backgrounds)
- [ ] Standalone-fallback script disables Run buttons when not in AI-Hydro preview
- [ ] File saved to workspace
- [ ] `show_html_preview(path)` called so it opens in the panel

If ANY box is unchecked, the module is not production-grade. Do not present it to the researcher until every box is checked.

---

# DESIGN PRINCIPLES (north star)

1. **Dark-first.** Background is always `#0a0a15` → `#1a1a2e` gradient.
2. **Cyan accent dominates.** Primary `#00A3FF`. Secondary `#00DDFF`. Warm tones forbidden except `#fbbf24` for warnings.
3. **Inline everything.** Single self-contained HTML file. Google Fonts loaded via CDN is the only external dependency.
4. **Bake synthetic data in.** First load must work without network. Real data only in the final Python cell, with a CSV fallback.
5. **One interactive per section.** Don't overwhelm. Explain → interact → reflect.
6. **Progressive complexity.** Start with visual intuition, end with real computation.
7. **Every quiz question teaches.** Wrong answers should explain why they're wrong, not just be marked red.
8. **Credible by construction.** Citation + provenance + license + named authors on every artifact. No "trust me" content.
