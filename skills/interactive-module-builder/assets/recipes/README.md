# Verified recipe cookbook

Each file here is a **known-good, copy-paste** snippet for one AI-Hydro interactivity primitive.
They are the canonical source of truth for the contracts described in `../../SKILL.md` and double as
regression fixtures: if a primitive's contract changes in the bridge, update the matching recipe here.

| Recipe | Primitive | What it shows |
|---|---|---|
| `bindparam-cell.html` | `bindParam` + Python cell | slider re-substitutes `{{name}}` in cell source, auto-runs |
| `timeline.html` | `timeline` | play/pause/scrub driving a canvas redraw |
| `compare.html` | `compare` | before/after wipe over two images |
| `sim-loop.html` | `sim` | rAF canvas loop reading a live slider |
| `plotly-chart.html` | `plot` | branded Plotly flow-duration curve |
| `three-terrain.html` | `scene3d` | draggable three.js DEM surface |
| `manim-scene.py` | Manim video cell | a short `Scene` subclass body |

## Rules baked into these recipes (do not break)

- Every JS primitive is called inside a `whenReady(...)` guard — `window.aihydro` is injected after
  module scripts may run.
- No hardcoded `three.js`/Plotly `<script>` tag. `scene3d` pins `three@0.128.0` (last UMD
  OrbitControls release); `plot` lazy-loads Plotly from the CSP-whitelisted CDN. Never use
  `examples/jsm/` or `@latest`.
- Snippets are fragments meant to drop into the canonical module skeleton — they are not full
  documents and intentionally omit the hero/provenance/license furniture.

```html
<!-- The readiness guard every recipe assumes is present once per module: -->
<script>
function whenReady(fn){
  if (window.aihydro) return fn(window.aihydro);
  var n = 0, id = setInterval(function(){
    if (window.aihydro || ++n > 100) { clearInterval(id); if (window.aihydro) fn(window.aihydro); }
  }, 50);
}
</script>
```
