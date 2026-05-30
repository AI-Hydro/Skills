---
name: hydro-mcp-tool-builder
description: Guide the agent to create new AI-Hydro MCP tools — Python @mcp.tool() functions that extend the platform's hydrological analysis capabilities. Use when the user wants to add a new tool, wrap a hydrology library, expose a new data source, or build a custom analysis function for the AI-Hydro MCP server.
when_to_use: When the user asks to "add a tool", "create an MCP tool", "wrap this library as a tool", "expose X to the agent", or wants to extend AI-Hydro's analysis capabilities with a new Python function
domain: development
tools_used:
  - list_available_tools
  - describe_tool
  - aihydro_describe_capability
tags:
  - mcp
  - tool-development
  - python
  - extensibility
  - tiers
  - authoring
---

# AI-Hydro MCP Tool Builder

Guide for creating new `@mcp.tool()` functions that extend AI-Hydro's hydrology
capabilities. The MCP server is a Python FastMCP app (the `aihydro-tools`
package); tools are decorated functions the agent calls during conversations.

Follow these conventions and your tool is **born compliant** — it gets correct
context-injection (hot vs summary), argument-repair, self-correcting errors, and
session resolution for free. The full canonical reference is
`knowledge/tools/AUTHORING_GUIDE.md` in the `aihydro-tools` repo (loadable live
as the `mcp-tool-authoring` skill); this skill is the working playbook.

> Design for a **weak driving model**: it guesses parameter names and loops on
> errors. Your job is to make the right call obvious and the wrong call
> self-correcting.

## When This Workflow Applies

- Add a new analysis capability (e.g., "add an IDF curve tool")
- Wrap an existing hydrology library (pysheds, hydrofunctions, neuralhydrology…)
- Expose a new data source (GRDC, BOM, Environment Canada…)
- Build a custom computation the agent can invoke

## Step 0 — Should this be a tool at all? (decision gate)

Answer first — most "new tool" requests are really a skill or a parameter.

1. **One atomic, verifiable action?** A multi-step pipeline is a **skill**, not a
   tool. Reference knowledge the model reasons *with* is **package knowledge**.
   (The three primitives: MCP tool / skill / package knowledge.)
2. **Has the simpler layer demonstrably failed?** Adding a tool requires a
   documented failure (a benchmark or session trace), not a hypothetical —
   tool count grew 11 → 56 → ~100 without this discipline.
3. **Which tier?** (set in `ai_hydro/mcp/app.py::TOOL_TIERS`, numeric 1/2/3):
   - Returns a number a hydrologist could cite/argue about → **Tier 1**
     (auto-`hot`; gets a post-run validator). When in doubt, Tier 1.
   - Data fetch / workflow → **Tier 2**. Infra / state / discovery → **Tier 3**.
4. **Will it run > ~30 s, or run in parallel, or need cancelling?** Then it must
   be a **job**, not a blocking call — see Step 6.

If 1–2 don't clear the gate, stop.

## Step 1 — Where the tool lives

Tools are `@mcp.tool()` functions in `ai_hydro/mcp/tools_<domain>.py` (e.g.
`tools_analysis.py`, `tools_session.py`, `tools_modelling.py`, `tools_map.py`,
`tools_indices.py`, …). Browse the live surface before adding — don't duplicate:

```text
list_available_tools()                  → every registered tool name
aihydro_describe_capability("watershed")→ one line per tool in a domain
describe_tool("compute_twi")            → full schema + worked example
```

Put your function in an existing `tools_*.py` if it fits a domain, else create a
new `tools_<domain>.py`.

### What does it connect to?

| If it needs… | Use |
|---|---|
| USGS/NWIS data | `dataretrieval` (core dep) |
| Spatial/raster | `pysheds`, `rasterio`, `xarray` (`[analysis]` extra) |
| Statistics | `scipy.stats`, `numpy`, `pandas` (core) |
| Machine learning | `torch`, `neuralhydrology` (`[modelling]` extra) |
| External API | `httpx` / `aiohttp` |
| Pure computation | no extra deps |

## Step 2 — Naming + parameters (so repair + injection behave)

**Name**: verb-first snake_case (`compute_*`, `fetch_*`, `extract_*`, `list_*`,
`get_*`). The name prefix decides the tool's domain bucket — match an existing
prefix in `tools_discovery.py::_DOMAIN_PREFIXES`.

**Parameters**: use **canonical names** so the argument-repair middleware routes
the weak model's guesses to the right key. Known canonical names (with their
auto-aliases): `index_name`, `geometry`, `gauge_id`, `session_id`, `latitude`,
`longitude`, `start`, `end`, `frequency`, `resolution`. If your param is a
synonym, rename it to the canonical one; if it's genuinely new and mis-nameable,
add an alias to `_GLOBAL_ALIASES`.

- **Always add type hints** (`str`, `int`, `float`, `bool`, `list[str]`) — they
  become the JSON schema that drives coercion (`"28.2"`→`28.2`, `"B4"`→`["B4"]`)
  and the self-help schema shown on failure.
- **Required = no default; optional = sensible default** (usually `None`).
- Keep the signature **flat** (scalars + `list[str]`). Avoid nested dict params —
  the weak model fills those poorly and repair can't help.

## Step 3 — Write the tool

```python
from __future__ import annotations
from ai_hydro.mcp.app import mcp
from ai_hydro.mcp.helpers import _resolve_session, _maybe_set_workspace
from ai_hydro.session import HydroSession


@mcp.tool()
def compute_drought_index(
    session_id: str | None = None,
    index_name: str = "SPI",
    window_months: int = 3,
) -> dict:
    """Compute a drought index (SPI, SPEI, PDSI) for the bound study; returns monthly series + severity class.

    Use when the user asks about drought severity, dry spells, or low-flow
    conditions. SPI = precip only, SPEI = precip+temp, PDSI = full water balance.

    Args:
        session_id: Resolved automatically if omitted (active session).
        index_name: "SPI" | "SPEI" | "PDSI". Default SPI.
        window_months: Aggregation window — 3 seasonal, 12 annual.
    """
    session_id = _resolve_session(session_id, None)   # chat binding → auto → fallback
    session = HydroSession.load(session_id)
    _maybe_set_workspace(session)                     # if the tool writes files

    cached = session.get("drought")                   # NOTE: .get(slot) / .set(slot, value)
    if cached:                                         # there is NO get_slot()/set_slot()
        return {**cached, "_cached": True}

    # ... deterministic computation ...
    result = {"index_name": index_name, "window_months": window_months, "summary": {}}

    session.set("drought", result)
    return result
```

### Key conventions

- **Session**: resolve with `_resolve_session(session_id, None)`; read/write slots
  with `session.get(slot)` / `session.set(slot, value)` (dynamic slots — plugins
  may add their own). For admin/query tools that must NOT auto-create, pass
  `_resolve_session(..., allow_auto_create=False)`.
- **First docstring line** is the *entire* summary the agent sees for non-hot
  tools — make it a self-contained, action-first sentence, < ~100 chars, naming
  common valid values. No leading blank line.
- **Errors**: raise a typed `ToolError` / `SessionResolutionError` (with
  `recovery` + `next_tools`) — the middleware turns exceptions into self-help
  payloads (correct schema + corrected example). Never return a bare stack trace.
- **Output**: a lean JSON `dict`. Reference large arrays by a `_data_file`
  pointer; don't dump megabytes of series into the response.

## Step 4 — Set the tier and register

1. **Tier** — add the name to `ai_hydro/mcp/app.py::TOOL_TIERS` (Tier 1 if it
   produces a citable result). Tier 1 is automatically `hot` (full schema
   injected). Only add to `HOT_TOOL_ALLOWLIST` if the tool is called in nearly
   every session — **don't** make a tool hot "to help" the model; that bloats
   every prompt. Everything else is one `describe_tool` away.
2. **Register** — import the module in `ai_hydro/mcp/__init__.py`:
   ```python
   from . import tools_drought  # triggers @mcp.tool() registration
   ```
   Community plugins instead declare an entry point:
   ```toml
   [project.entry-points."aihydro.tools"]
   compute_drought_index = "my_pkg.module:compute_drought_index"
   ```
3. **Tier-1 only** — register a post-run validator in `__init__.py` via
   `register_post_validator(name, validator_fn, kwargs_builder)`.

You do **not** set `_meta` yourself — `_tag_tools_with_tier_meta()` stamps
`tier`/`domain`/`hot` after registration.

## Step 5 — Test

```bash
# Smoke: is it registered?
python -c "
import asyncio
from ai_hydro.mcp.app import mcp
print([t.name for t in asyncio.run(mcp.list_tools())])
"
# Full suite:
python -m pytest tests/test_mcp_integration.py -v -m "not live"
```

Add a registration assertion + a smoke call to `tests/test_mcp_integration.py`.

## Step 6 — Long-running tools must be jobs (not blocking calls)

If the tool can exceed ~30 s, run in parallel, or need cancelling, **do not
block** the MCP call. Kick off detached work and return a `job_id` immediately,
then expose poll/result tools. The live pattern is in `tools_modelling.py`:

```python
import subprocess, sys, uuid, json
from pathlib import Path

job_id = uuid.uuid4().hex[:12]
artifact_dir = Path.home() / ".aihydro" / "jobs" / job_id
artifact_dir.mkdir(parents=True, exist_ok=True)
(artifact_dir / "job_config.json").write_text(json.dumps(config))
proc = subprocess.Popen(
    [sys.executable, "-m", "my_pkg.runner", str(artifact_dir)],
    start_new_session=True,
)
# PERSIST proc.pid so the job can be cancelled later.
return {"job_id": job_id, "status": "pending", "log_path": str(artifact_dir / "job.log")}
```

The runner writes `status.json` checkpoints; a `get_<thing>_status(job_id)` tool
polls them. (A shared `ai_hydro/mcp/jobs.py` with start/status/result/**cancel**
is the planned generalization — see `AGENT_EXECUTION_MODEL.md`.)

## Common Hydrology Libraries to Wrap

| Library | What it does | Tool idea |
|---|---|---|
| `hydrofunctions` | NWIS data access | covered by `fetch_streamflow_data` |
| `pysheds` | Flow direction, accumulation | extend `delineate_watershed` |
| `standard-precip` | SPI computation | `compute_drought_index` |
| `baseflow` | Digital filter separation | extend `extract_hydrological_signatures` |
| `neuralhydrology` | LSTM/Transformer rainfall-runoff | covered by `train_hydro_model` |
| `pyet` | PET estimation (20+ methods) | `estimate_pet` |
| `xclim` | Climate indices, IDF curves | `compute_climate_indices` |
| `flopy` | MODFLOW groundwater modelling | `setup_groundwater_model` |

## Anti-Patterns

- **Don't hardcode a multi-step pipeline as one mega-tool.** That's a skill.
- **Don't make a tool hot to "help" the model.** It bloats every session.
- **Don't block on long work.** Make it a job (Step 6).
- **Don't use `session.set_slot`/`get_slot`** — they don't exist. It's
  `session.get(slot)` / `session.set(slot, value)`.
- **Don't return raw DataFrames or huge arrays.** Return JSON dicts; summarize
  series (min/max/mean/percentiles) or reference a file.
- **Don't swallow exceptions.** Raise `ToolError` with a helpful message.
- **Don't require local file paths.** Work from `gauge_id`/coordinates/session.
- **Don't duplicate existing tools.** Check `list_available_tools()` /
  `get_session_summary()` first.

## Pre-merge checklist

- [ ] Cleared the Step 0 gate (atomic action; documented need; tier chosen).
- [ ] Name is verb-first snake_case matching a `_DOMAIN_PREFIXES` prefix.
- [ ] First docstring line is a self-contained one-liner.
- [ ] Every param typed; canonical names used (or alias added).
- [ ] `session_id` via `_resolve_session`; slots via `.get`/`.set`.
- [ ] Tier set in `TOOL_TIERS`; `HOT_TOOL_ALLOWLIST` only if truly high-frequency.
- [ ] Long-running → job with persisted PID.
- [ ] Lean JSON dict; large arrays referenced by file pointer.
- [ ] Module imported in `__init__.py` (or entry-point declared).
- [ ] Tier-1 only: post-run validator registered.
- [ ] Test added; `pytest -m "not live"` passes.
