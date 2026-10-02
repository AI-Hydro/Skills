---
name: flood-inundation-lead
description: Autonomous lead loop (RALP) for defensible flood inundation mapping in AI-Hydro — HAND+SRC, validation, map UX, and phased delivery
when_to_use: When executing the flood inundation plan, running a RALP iteration, or the user says "lead loop", "continue flood work", or "next inundation iteration"
domain: composition
tools_used:
  - delineate_watershed
  - compute_flood_frequency
  - compute_design_hydrograph
  - map_flood_inundation
  - map_flood_inundation_hydrograph
  - run_inundation_physics_validation
  - wait_for_job
  - get_inundation_physics_result
  - export_inundation_surrogate_dataset
  - train_inundation_surrogate
  - get_inundation_surrogate_result
  - map_show
  - map_add_layer_from_run
  - add_claim
  - run_skeptic
  - run_python
tags:
  - flood
  - inundation
  - HAND
  - RALP
  - map
  - defensibility
---

# Flood Inundation Lead Loop (RALP)

## Purpose

Execute one iteration of the flood inundation plan autonomously: research forks, decide with a scored rubric, build the smallest shippable slice, validate, UX-review, integrate to map, and gate phase advancement.

## Before every iteration

1. Read `MCP/aihydro-tools/docs/flood_inundation/STATUS.md`
2. Read last 5 rows of `MCP/aihydro-tools/docs/flood_inundation/DECISION_LOG.md`
3. Read `.cursor/plans/flood_inundation_mapping_3f58207e.plan.md` (current phase section)

## RALP cycle (7 steps)

1. **RESEARCH** — If the next todo has a fork, web-search 2–3 options + scan codebase.
2. **DECIDE** — Score each option 1–5 on: Defensibility (25%), Global (20%), UX (20%), Build cost (15%), Vision (10%), Practical demand (10%). Log winner to DECISION_LOG.md.
3. **BUILD** — Smallest complete diff for the top pending todo in STATUS.md.
4. **VALIDATE** — `pytest` for touched paths; HRB tasks for the phase; hindcast CSI when applicable.
5. **UX REVIEW** — Jobs checklist: scrubber, summary card, caveat chip, click-to-inspect depth, colorblind ramp.
6. **INTEGRATE** — Map push + claim draft + provenance chip when a tool ships.
7. **GATE** — Update STATUS.md; advance phase only when exit criteria pass.

## Hard vetoes (never auto-pick)

- Single crisp flood boundary with no uncertainty band (Phase 1+)
- Map layer without scope/caveat metadata
- Numeric claim without `_run_id` / citation grammar
- Heavy new dependency before a lighter alternative is tried

## Escalate to user when

- Paid API keys or restricted-licence exposure datasets needed
- Scope expansion to pluvial/coastal/coastal surge
- Same blocker fails 3 iterations
- Breaking map UX change

## Defaults (no user input required)

- Demo basin: USGS `01031500`
- Exposure: OSM + WorldPop/HRSL (document licence in claim)
- Viz path: deck.gl extension first; Cognaterra 3D in Phase 4
- Physics tier: SFINCS via HydroMT (not HEC-RAS GUI)

## End-of-iteration report format

```
Phase: N
Shipped: ...
Tests: ...
Next todo: ...
Blockers: none | ...
```
