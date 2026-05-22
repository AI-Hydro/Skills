# Contributing a Skill

Thank you for contributing to the AI-Hydro Skills marketplace!

## Skill Format

Each skill lives in `skills/<your-skill-id>/` and requires two files:

### `SKILL.md`

```markdown
---
name: your-skill-id
description: One sentence describing what this skill does
when_to_use: When should the agent apply this skill? Be specific.
domain: frequency-analysis | baseflow | modelling | interpretation | general
tools_used:
  - fetch_streamflow_data   # list AI-Hydro MCP tools used
tags:
  - tag1
  - tag2
---

# Skill Title

## Purpose
...

## Step 1 — ...
...
```

### `manifest.json`

```json
{
  "id": "your-skill-id",
  "name": "Human-readable Name",
  "description": "One sentence for the marketplace card.",
  "version": "0.1.0",
  "author": "Your Name",
  "domain": "frequency-analysis",
  "category": "analysis",
  "icon": "graph-line",
  "tags": ["tag1", "tag2"],
  "tools_used": ["fetch_streamflow_data"],
  "when_to_use": "When the user asks about ...",
  "github_url": "https://github.com/AI-Hydro/Skills/tree/main/skills/your-skill-id",
  "skill_url": "https://raw.githubusercontent.com/AI-Hydro/Skills/main/skills/your-skill-id/SKILL.md"
}
```

## Submission Checklist

- [ ] `SKILL.md` has a valid YAML frontmatter block
- [ ] `when_to_use` is specific enough for the agent to trigger correctly
- [ ] Workflow steps are actionable (code examples preferred)
- [ ] `manifest.json` fields are all filled in
- [ ] Tested by installing locally and asking the agent a relevant question

## Submitting

[Open an issue](https://github.com/AI-Hydro/Skills/issues/new?template=new_skill.md) with your skill attached, or open a pull request directly adding `skills/<your-skill-id>/`.

## Domains

| Domain | Use for |
|---|---|
| `frequency-analysis` | Return periods, flood frequency, extreme value |
| `baseflow` | Baseflow separation, recession, groundwater |
| `modelling` | Model selection, calibration, validation |
| `interpretation` | Reading results, comparing catchments |
| `composition` | Multi-step workflows that span several tools |
| `general` | Anything else |
