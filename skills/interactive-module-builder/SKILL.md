---
name: interactive-module-builder
description: Create production-grade AI-Hydro interactive learning modules — self-contained HTML files with executable Python cells, sliders, quizzes, scrollytelling, real AI-Hydro branding (animated gradient droplet logo, dark theme, cyan accent, Poppins/Nunito/Quicksand fonts), peer-reviewed citations, full provenance footer, and CC-BY-4.0 license. Modules open automatically in AI-Hydro's built-in HTML Preview panel (which supports Python/JS cell execution); do NOT assume an external browser. Use when the user asks to create a learning module, tutorial, interactive lesson, educational artifact, or "explain X with visuals" for any hydrology topic.
when_to_use: When the user asks to create a module, interactive module, learning module, tutorial, interactive lesson, educational content, educational artifact, "explain X with visuals", "make a module about", "create a tutorial for", "build an interactive lesson on", "create something interactive", or build any educational or teaching material about a hydrology topic. Also use when the user wants to produce content that combines explanations with executable Python code or interactive visualizations.
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

### CSS isolation — critical

**DO NOT define CSS for any of these bridge-owned classes in your module `<style>` block:**

`.aihydro-cell` · `.aihydro-cell-header` · `.aihydro-source` · `.aihydro-output` · `.aihydro-run` · `.aihydro-copy` · `.aihydro-toggle-source` · `.aihydro-standalone-pill`

These are injected by the bridge and styled consistently. Overriding them breaks the dark theme and toggle-collapse behavior. Your module `<style>` block should only define: hero, strip, callouts, provenance footer, quiz, and truly module-specific layout.

---

# PYTHON CELL RULES — READ BEFORE WRITING ANY CELL

## Kernel setup — DO NOT override (CRITICAL)

The AI-Hydro HTML Preview kernel pre-configures the Python environment before running any cell. These things are already done for you — adding them yourself causes warnings and conflicts:

| ❌ DO NOT add to cells | ✅ Why it's handled for you |
|---|---|
| `import matplotlib; matplotlib.use('Agg')` | Kernel sets Agg backend at startup |
| `plt.show()` | Kernel auto-captures all open figures after every cell run |
| `import warnings; warnings.filterwarnings(...)` | Kernel already filters FigureCanvasAgg and switching-backend warnings |

**Correct pattern:**
```python
# ✓ Just import and use — kernel handles backend and figure capture
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.rcParams.update({ ... })
fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(...)
plt.tight_layout()
# ← no plt.show() needed
```

**Wrong pattern (DO NOT use):**
```python
import matplotlib
matplotlib.use('Agg')          # ← emits "backend already set" warning
import matplotlib.pyplot as plt
...
plt.show()                     # ← emits FigureCanvasAgg non-interactive warning
```

## Modules MUST be self-contained — no file I/O

Modules are opened in a kernel with a different working directory than the user's workspace. `os.path.exists("some_file.geojson")` will almost always be False, and loading external files is fragile and breaks offline use.

**Rule:** All data must be embedded as Python constants inside the cell. Never use file I/O in module cells. Never check for local files and fall back.

```python
# ✓ CORRECT — data embedded as constant
WATERSHED_COORDS = [[-69.5, 45.0], [-69.2, 45.0], ...]

# ❌ WRONG — fragile file I/O
with open('watershed.geojson') as f:
    data = json.load(f)
# Then: KeyError when file doesn't exist or has unexpected structure
```

## Matplotlib color constraint (CRITICAL — violating this crashes cells)

NEVER use CSS `rgba()` format strings in any matplotlib call. Matplotlib does not understand CSS syntax.

```python
# WRONG — crashes with ValueError: Invalid RGBA argument
ax.set_facecolor('rgba(10,10,21,1)')
spine.set_color('rgba(125,211,252,0.18)')

# CORRECT — use hex or RGBA tuple (values 0-1, NOT 0-255)
ax.set_facecolor('#0a0a15')                           # opaque hex
spine.set_color((125/255, 211/255, 252/255, 0.18))    # RGBA tuple
plt.setp(ax.spines.values(), color=(125/255, 211/255, 252/255, 0.18))
```

This affects every matplotlib call that accepts a color: `set_color()`, `set_facecolor()`, `set_edgecolor()`, `tick_params()`, `ax.spines.values()`, `ax.set_xlabel(label, color=...)`, etc. Always use hex or tuple. Never CSS `rgba()`.

## Canonical dark matplotlib boilerplate (include at top of every matplotlib cell)

```python
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

mpl.rcParams.update({
    'figure.facecolor': '#0a0a15',
    'axes.facecolor':   '#0f0f1e',
    'axes.edgecolor':   (125/255, 211/255, 252/255, 0.30),
    'axes.labelcolor':  '#7dd3fc',
    'xtick.color':      '#94a3b8',
    'ytick.color':      '#94a3b8',
    'text.color':       '#e2e8f0',
    'grid.color':       (125/255, 211/255, 252/255, 0.10),
    'legend.facecolor': '#1a1a2e',
    'legend.edgecolor': (125/255, 211/255, 252/255, 0.25),
})
```

This ensures correct dark-theme rendering for axes text, labels, ticks, and spines without per-axes overrides.

## Cell length and figure sizing

- Target 25 lines or fewer per cell. The bridge auto-collapses cells with more than 20 lines — a compact cell shows its output without requiring the researcher to expand code first.
- Split setup from visualization: one "compute" cell (parameters + algorithm) and one "plot" cell (figure only, < 20 lines). The output figure then appears immediately after the short plot cell.
- `figsize` constraint: max `(11, 5)` for a single panel, `(14, 5)` for two panels. Never exceed `(16, 5)` — the iframe column clips wider figures. Always call `plt.tight_layout()`.
- Axis labels always need `color=` if not using rcParams boilerplate: `ax.set_xlabel('Day', color='#7dd3fc')`.

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

# CITATIONS — MANDATORY WORKFLOW (anti-hallucination)

> **CRITICAL RULE: NEVER invent or guess a DOI. Every citation must come from a verified API call.**

## Citation lookup procedure

For **every** non-trivial method or dataset reference in a module:

1. **Call `lookup_citation(query, source_hint?)`** with the paper title or "Author Year".
2. If the tool returns a result → use the `formatted_apa` string and `doi` exactly as returned.
3. If the tool returns `null` or `not_found` → write:
   > *No peer-reviewed citation found for this method.*
   Do **NOT** fall back to guessing, paraphrasing from memory, or inserting a plausible-sounding DOI.

```
# Example agent workflow:
result = lookup_citation("Beven Kirkby 1979 topographic wetness index")
# → { doi: "10.1080/02626667909491834", formatted_apa: "Beven, K.J. & Kirkby, M.J. (1979)..." }
```

## Why this matters
The old approach (hardcoded ~10-entry lookup table) led to DOI hallucination for anything outside the table. The `lookup_citation` MCP tool queries CrossRef → Semantic Scholar → DataCite in cascade and caches results in `~/.aihydro/citations/`. It is always more accurate and current than any static list.

---

# INTERACTIVE MAPS — data-aihydro-map contract

When a module needs an interactive Leaflet map, use the **3-line standardised contract** below.
Do **NOT** write `<script src="https://cdn.jsdelivr.net/npm/leaflet...">` or manual `L.map(...)` code.
The AI-Hydro Bridge adapter initialises the map automatically from `data-*` attributes.

## Author template (copy verbatim, fill in values)

```html
<div class="aihydro-map"
     data-aihydro-map-id="unique-id-for-this-map"
     data-basemap="usgs-topo"
     data-initial-zoom="10"
     style="width:100%; height:500px;">
  <script type="application/geo+json">
    { "type": "FeatureCollection", "features": [...] }
  </script>
</div>
```

## Supported `data-basemap` values
| Value | Description |
|---|---|
| `usgs-topo` | USGS National Map topo (default) |
| `usgs-imagery` | USGS satellite imagery |
| `esri-satellite` | ESRI World Imagery |
| `carto-dark` | CARTO dark basemap |
| `osm` | OpenStreetMap |

## Optional attributes
| Attribute | Purpose |
|---|---|
| `data-initial-zoom` | Numeric zoom level (default: auto-fit to GeoJSON bounds) |
| `data-center-lat` / `data-center-lng` | Override map centre |
| `data-marker-lat` / `data-marker-lng` | Add a styled gauge/point marker |
| `data-marker-label` | Popup label for the marker |
| `data-gauge-id` | USGS gauge ID shown in the marker popup |
| `data-style-color` | Boundary stroke colour (default: `#00DDFF`) |
| `data-style-fill` | Fill colour (default: `#00A3FF`) |
| `data-style-fill-opacity` | Fill opacity (default: `0.08`) |

## What the bridge does automatically
- Loads Leaflet 1.9.4 on demand (no CDN tag needed in the module)
- Applies AI-Hydro dark palette (consistent across all modules)
- Parses inline `<script type="application/geo+json">` child and renders GeoJSON overlay
- Auto-fits bounds unless `data-center-lat/lng` is set
- Adds layer toggle control, scale bar, and AI-Hydro watermark
- Emits `map.event` PreviewEvents so the agent can observe map interactions

## Module-specific additions
If you need a custom overlay (e.g. a canvas-based TWI raster), access the map object after
the bridge initialises it via `mapEl._aihydroMap`:

```javascript
var mapEl = document.querySelector('.aihydro-map[data-aihydro-map-id="your-id"]');
function addCustomOverlay() {
  if (!mapEl._aihydroMap || !window.L) { setTimeout(addCustomOverlay, 150); return; }
  // L.imageOverlay(...).addTo(mapEl._aihydroMap);
}
setTimeout(addCustomOverlay, 500);
```

---

# INTERACTIVITY PRIMITIVES — the `window.aihydro` API

Beyond Python cells and maps, the bridge ships a small set of **author-facing JS primitives** on
the global `window.aihydro` object. They are pure DOM (no kernel dependency), respect
`prefers-reduced-motion`, and carry the AI-Hydro dark palette automatically. **Use these instead of
hand-rolling animation, charts, or 3D** — they are the only contracts the bridge guarantees, and the
validator checks for their correct use.

> **Copy-paste recipes:** verified, pinned snippets for every primitive below live in
> `assets/recipes/` (one file per primitive + a `README.md`). Start from the recipe rather than
> writing a primitive call from memory.

## How to call them (timing matters)

`window.aihydro` is injected by the bridge *after* your module's inline `<script>` may have already
run. Always guard with a readiness poll — never assume `window.aihydro` exists at parse time:

```html
<script>
  function whenReady(fn){
    if (window.aihydro) return fn(window.aihydro);
    var n = 0, id = setInterval(function(){
      if (window.aihydro || ++n > 100) { clearInterval(id); if (window.aihydro) fn(window.aihydro); }
    }, 50);
  }
  whenReady(function(aihydro){
    aihydro.quiz();
    aihydro.compare('.aihydro-compare');
    // ...wire the rest of this module's primitives here...
  });
</script>
```

## The primitive → pedagogy decision matrix

Pick the primitive that matches the *cognitive job*, not the one that looks flashiest. One
interactive per section (Design Principle #5).

| Pedagogical goal | Primitive | Why this one |
|---|---|---|
| "Change a parameter, see the equation/figure respond" | **`bindParam`** + Python cell | Real computation; the figure is authoritative, not a cartoon |
| "Watch a process evolve over time" (recession, wave routing, infiltration front) | **`timeline`** | Play/pause/scrub; can drive a cell frame-by-frame |
| "Compare two states" (pre/post dam, calibrated vs. observed, DEM vs. TWI) | **`compare`** | Before/after wipe reads instantly; no legend needed |
| "Feel a continuous dynamic in real time" (rain → runoff response) | **`sim`** | 60 fps canvas; cheap, no kernel round-trip |
| "Explore multi-series quantitative data" (flow-duration, hydrographs, scatter) | **`plot`** | Branded Plotly; hover/zoom for free |
| "Understand 3D structure" (terrain, watershed surface, DEM/TWI relief) | **`scene3d`** | Draggable three.js; the only honest way to show relief |
| "Cinematic, narrated concept animation" (3blue1brown-style) | **Manim video cell** | Pre-rendered MP4; precise typographic math animation |
| "Reveal an answer / hide a derivation" | **`reveal`** | Progressive disclosure without leaving the page |
| "Drive a story as the reader scrolls" | **`scrolly`** | Ties narrative beats to viewport position |

**Anti-patterns:** don't use `sim` for anything quantitative the reader must read off an axis (use a
cell or `plot`); don't use `scene3d` for 2D data (use a figure); don't use a Manim video where a live
`bindParam` cell would let the reader experiment.

## Contracts (copy verbatim, fill values)

### `bindParam` — slider → live cell parameter
The cell's `<pre class="aihydro-source">` is a template with `{{name}}` placeholders re-substituted on
every input change. Values persist across reloads automatically.

```html
<label>α <input id="alpha" type="range" min="0.9" max="0.99" step="0.005" value="0.925"></label>
<span data-aihydro-mirror="alpha">0.925</span>
<!-- cell source contains:  alpha = {{alpha}}  -->
<script>whenReady(function(a){ a.bindParam({ from:'#alpha', cellId:'bfi-cell', name:'alpha', autorun:true }); });</script>
```

### `timeline` — play / pause / step / scrub
```html
<div id="tl"></div>
<script>whenReady(function(a){
  a.timeline({ mount:'#tl', steps:60, fps:12, autoplay:true,
    onTick:function(i, t){ /* t in [0,1] — redraw a canvas, advance a marker */ },
    // optional: drive a Python cell frame-by-frame
    cellId:'wave-cell', param:'frame' });
});</script>
```

### `compare` — before/after wipe
First child = "before", second = "after". Children must be equal-sized (images, canvases, or figures).
```html
<div class="aihydro-compare" style="height:320px">
  <img src="data:image/png;base64,...before...">
  <img src="data:image/png;base64,...after...">
</div>
<script>whenReady(function(a){ a.compare('.aihydro-compare'); });</script>
```

### `sim` — requestAnimationFrame canvas loop
```html
<canvas data-aihydro-sim id="rain" width="640" height="240"></canvas>
<script>whenReady(function(a){
  a.sim({ canvas:'#rain', autoplay:true,
    params:function(){ return { rain:+document.querySelector('#rainSlider').value }; },
    step:function(ctx, t, p){ /* ctx is a 2D context; draw using p.rain and t (seconds) */ } });
});</script>
```

### `plot` — branded Plotly
Plotly loads lazily from the CSP-whitelisted CDN; the AI-Hydro dark palette is applied unless you
override `layout`.
```html
<div id="fdc" style="height:360px"></div>
<script>whenReady(function(a){
  a.plot({ mount:'#fdc',
    data:[{ x:[/*...*/], y:[/*...*/], type:'scatter', mode:'lines', name:'Flow-duration' }],
    layout:{ xaxis:{ title:'Exceedance %' }, yaxis:{ title:'Q (m³/s)', type:'log' } } });
});</script>
```

### `scene3d` — draggable three.js scene
`ctx = { THREE, scene, camera, renderer, controls, canvas, dem }`. Returns a promise resolving to `ctx`.
```html
<canvas data-aihydro-scene3d id="terrain"></canvas>
<script>whenReady(function(a){
  a.scene3d({ canvas:'#terrain', dem:DEM_GRID /* 2D array of heights */,
    setup:function(ctx){
      var g = new ctx.THREE.PlaneGeometry(4, 4, ctx.dem.length-1, ctx.dem[0].length-1);
      /* displace vertices by ctx.dem, add a MeshStandardMaterial, ctx.scene.add(mesh) */
    } });
});</script>
```

**Pinned-version rule (do not change):** the bridge loads `three@0.128.0` — the last release that
ships the legacy UMD `examples/js/controls/OrbitControls.js`. **Never** hardcode a `three` `<script>`
tag yourself, and never reference `examples/jsm/` ESM paths or a floating `@latest` version: r134+ is
ESM-only and the controls 404, which silently leaves the canvas black. Let `scene3d` own three.js.

---

# MANIM VIDEO CELLS (3blue1brown-style animation)

For cinematic, narrated concept animations, author a **video-render cell**: a normal Python cell that
defines a Manim `Scene`, marked so the kernel renders it to an MP4 and plays it inline.

## Contract

- Add `data-aihydro-render="video"` to the `.aihydro-cell` (or use `data-language="manim"`).
- The cell body is ordinary Python that defines one or more `class …(Scene)` with a `construct(self)`.
- Do **not** call `manim` from the command line, write files, or set output paths — the kernel finds
  every `Scene` subclass in the cell, renders it at low quality to a temp MP4, base64-encodes it, and
  the bridge plays it in a `<video controls>` element.

```html
<div class="aihydro-cell" data-aihydro-cell-id="twi-anim" data-language="python" data-aihydro-render="video">
  <div class="aihydro-cell-header">
    <span class="aihydro-cell-lang">manim</span>
    <span class="aihydro-cell-desc">Animated build-up of the TWI definition</span>
    <button class="aihydro-run" type="button">Run ▶</button>
  </div>
  <pre class="aihydro-source">from manim import *

class TwiScene(Scene):
    def construct(self):
        eq = MathTex(r"\\mathrm{TWI} = \\ln\\!\\left(\\frac{a}{\\tan\\beta}\\right)")
        eq.set_color("#00DDFF")
        self.play(Write(eq))
        self.wait(1)
</pre>
  <div class="aihydro-output" aria-live="polite"></div>
</div>
```

## Rules and graceful degradation

- **Manim is an optional kernel dependency.** If `manim`/`ffmpeg` aren't installed, the cell does not
  crash — the kernel appends a "Manim is not installed in this kernel environment" note to stderr.
  Treat Manim cells as enrichment, never as the only path to a concept.
- Keep scenes **short** (a few seconds) and low-complexity — rendering is synchronous on the host.
- Use the AI-Hydro palette inside scenes (`set_color("#00DDFF")`, background stays default dark).
- Every video cell **must** define at least one `class …(Scene)`; a video-render cell with no Scene
  renders nothing (the validator flags this).

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
2. **Self-review (mandatory):** Read back the saved file and verify the following before proceeding:
   - The `<script type="application/vnd.aihydro.module+json">` manifest is present and has all required fields
   - No Python cell contains `matplotlib.use(...)` or `plt.show()`
   - No Python cell uses file I/O (`open(...)`, `os.path.exists(...)`, `json.load(...)`)  
   - No matplotlib call uses CSS `rgba()` format strings — only hex or tuple `(r/255, g/255, b/255, alpha)`
   - Every `.aihydro-cell` has `data-aihydro-cell-id` (unique) + `data-language="python"`
   - Every cell's Run button is `<button class="aihydro-run" type="button">`
   - The provenance footer is present with all 5 rows
   - The References section has at least one peer-reviewed citation
   - If ANY issue is found: fix it in-place before calling `show_html_preview`.
3. Call `show_html_preview(file_path=...)` so the module opens automatically in the AI-Hydro HTML Preview panel (this is the built-in panel with Python cell execution; do not assume an external browser).
4. In your reply, surface the absolute path to the user and the topics covered.

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
- [ ] NO CSS `rgba()` strings used in any matplotlib call — hex or `(r/255, g/255, b/255, alpha)` tuples only
- [ ] Dark matplotlib rcParams boilerplate present at top of every matplotlib cell
- [ ] `ax.set_xlabel/ylabel` include `color=` argument (or rcParams covers it)
- [ ] `figsize` does not exceed `(14, 5)` for any cell — `plt.tight_layout()` present
- [ ] No module CSS overrides bridge-owned classes (`.aihydro-cell`, `.aihydro-source`, `.aihydro-output`, etc.)
- [ ] Standalone-fallback script disables Run buttons when not in AI-Hydro preview
- [ ] Any `window.aihydro` primitive (timeline/compare/sim/plot/scene3d/bindParam/quiz) is called inside a `whenReady(...)` guard — never at parse time
- [ ] No hardcoded `three.js`/Plotly `<script>` tag and no `examples/jsm/` or `@latest` CDN path — let `scene3d`/`plot` own their libraries (pinned `three@0.128.0`)
- [ ] Every `aihydro-sim`/`scene3d` canvas has a matching `aihydro.sim(...)`/`aihydro.scene3d(...)` call
- [ ] Every Manim video-render cell (`data-aihydro-render="video"`) defines at least one `class …(Scene)`
- [ ] NO `matplotlib.use(...)` or `plt.show()` in any cell (kernel handles both)
- [ ] NO file I/O (`open`, `os.path.exists`, `json.load`) in any cell — all data embedded as constants
- [ ] File saved to workspace
- [ ] **Self-review completed**: file re-read and all checklist items verified before `show_html_preview` is called
- [ ] **Linter clean**: run the **AI-Hydro: Validate Module** command (Command Palette) on the saved file — it deterministically checks the manifest, cell IDs/languages, `<code>`/`onclick`/`plt.show()`/`matplotlib.use()`/file-I/O/CSS-`rgba()` rules, and the provenance/license/references furniture. Resolve every reported error before publishing.
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
