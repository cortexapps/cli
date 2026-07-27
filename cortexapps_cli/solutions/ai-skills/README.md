---
name: AI Skills Catalog
description: Catalog your AI plugins and skills as first-class Cortex entities, with ownership and best-practice quality scorecards.
---

# AI Skills Catalog

Model your AI plugins and the skills they bundle (e.g. Claude Code plugins and Agent Skills) as Cortex entities — owned, scored, and discoverable just like your services.

## Overview

```
                              ┌──────────────────────┐
                              │      ai-plugin       │
                              │    docs-generator    │
                              └──────────┬───────────┘
                                         │
                                 ai-plugin-skills
               ┌─────────────────────────┴─────────────────────────┐
               ▼                                                   ▼
    ┌──────────────────────┐             │              ┌──────────────────────┐
    │       ai-skill       │             │              │       ai-skill       │
    │   changelog-writer   │             │              │     api-doc-sync     │
    └──────────┬───────────┘             │              └──────────┬───────────┘
               │                         │                         │
               └─────────────────────────┴─────────────────────────┘
                                         ▼
                       ai-plugin-service / ai-skill-service
                              ┌──────────────────────┐
                              │       service        │
                              │     docs-portal      │
                              └──────────────────────┘
```

Ownership is never duplicated onto the AI entities themselves — `ai-plugin-service` and `ai-skill-service` relationships point at a Service (or however you already model repos) that already carries an owning team in your Catalog. A skill's or plugin's owner is always "whoever owns the linked Service."

## What's Included

**Entity types:** `ai-plugin`, `ai-skill`

**Relationship types:**
- `ai-plugin-skills` — a plugin's bundled skills (plugin → skill)
- `ai-plugin-service` — the Service/repo that owns and hosts a plugin
- `ai-skill-service` — the Service/repo that owns a skill directly, for cases where a skill's ownership differs from its parent plugin's (e.g. distinct CODEOWNERS within a monorepo)

**Scorecard:** `ai-skills-quality` — 8 rules covering ownership (via the relationships above) and Anthropic's [Agent Skills authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices): concise SKILL.md (both this org's stricter target and Anthropic's hard limit), substantive descriptions within the spec's length bounds, no reserved words in the name, and shallow (one-level-deep) file references.

**Sample entities:** one plugin (`docs-generator`), two skills (`changelog-writer`, `api-doc-sync`), and one sample service (`docs-portal`) they're linked to — enough to see the shape without assuming anything about your real catalog.

## Installation

```
cortex solutions install -s ai-skills
```

## After Installing

**Populate quality data for real skills**

Three of the scorecard's rules — concise (`lineCount`), description length (`descriptionCharCount`, named to avoid confusion with the entity's own `description` field), and shallow references (`hasDeepReferences`) — read from Cortex custom metadata. `cortex ai-skills sync` pushes these via the Custom Data API. For each real skill you ingest:

```
cortex custom-data add --tag <skill-tag> --key lineCount --value <int>
cortex custom-data add --tag <skill-tag> --key descriptionCharCount --value <int>
cortex custom-data add --tag <skill-tag> --key hasDeepReferences --value <true|false>
```

The `cortex ai-skills sync` command computes and pushes all three automatically. Recompute on change, not on a timer — wire a GitHub Action or webhook to fire when a plugin/skill's files change, rather than recalculating on a fixed schedule. These values move maybe a couple of times a year; there's no reason to redo the work (or hit the git API) on every scorecard evaluation.

The sample entities above don't have these set, so they'll score lower on those three rules until you do — that's expected; they're there to show the entity/relationship shape, not a passing score.

**Link real plugins and skills to your own Services**

Point `ai-plugin-service` / `ai-skill-service` at whatever Service (or repository entity) already owns that code in your Catalog, instead of the sample `docs-portal`.

**Set up your AI Skills catalog**

Cortex Catalogs (the nav-level groupings like Services, Infrastructure, Domains) are UI-only today — there's no API or CLI support yet to script this step:

1. Go to [Catalogs](https://app.getcortexapp.com/admin/catalogs) → **New Catalog**
2. Relationship type: `ai-plugin-skills`
3. Root entity type: `ai-plugin`
4. Name it **AI Skills**

> Catalog creation will be automated once catalog API support is added to the CLI.
