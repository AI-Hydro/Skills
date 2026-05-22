# AI-Hydro Skills

Domain-specific workflow playbooks for the [AI-Hydro](https://github.com/AI-Hydro/AI-Hydro) VS Code extension. Skills are injected into the agent's system prompt and guide multi-step hydrological analyses.

## What is a Skill?

A Skill is a `SKILL.md` file that tells the AI-Hydro agent *how* to perform a specific hydrological workflow — step by step, with code examples, interpretation guidance, and common pitfalls. When a skill is installed and enabled, it becomes part of the agent's context for every conversation.

AI-Hydro Skills follow the **Agent Skills open standard** (SKILL.md format), compatible with Claude Code, Codex, Cursor, Cline, and Windsurf.

## Available Skills

| Skill | Domain | Description |
|---|---|---|
| [Flood Frequency Analysis](skills/flood-frequency-analysis/) | frequency-analysis | Fit GEV/LP3 distributions, compute return-period quantiles |
| [Baseflow Separation](skills/baseflow-separation/) | baseflow | Lyne-Hollick & Eckhardt filters, BFI, recession analysis |
| [Watershed Analysis Workflow](skills/watershed-analysis-workflow/) | composition | End-to-end catchment characterisation |
| [Model Selection Guide](skills/model-selection/) | modelling | HBV vs LSTM decision framework |
| [Calibration Diagnostics](skills/calibration-diagnostics/) | modelling | NSE/KGE/FDC diagnostics, residual analysis |
| [Signature Interpretation](skills/signature-interpretation/) | interpretation | Interpret BFI, FDC slope, seasonality, runoff ratio |

## Installing Skills

Open AI-Hydro → click the **Skills** toolbar button → **Marketplace** tab → Install.

Skills are stored globally at `~/.aihydro/skills/` and injected automatically into the agent's system prompt.

## Repository Structure

```
skills/
  <skill-id>/
    SKILL.md        ← workflow instructions (injected into agent)
    manifest.json   ← metadata for the marketplace
api/
  skills.json       ← auto-generated catalog (GitHub Pages)
.github/
  workflows/
    build-api.yml   ← regenerates skills.json on push
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) to author and submit your own skill.

## License

Skills are released under [CC-BY-4.0](LICENSE).
