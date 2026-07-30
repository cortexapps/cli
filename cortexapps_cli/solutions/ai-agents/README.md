---
name: AI Agents Catalog
description: Track internally-built AI agents as first-class Cortex entities, with ownership, model-adoption visibility, and a governance scorecard for engineering leaders.
---

# AI Agents Catalog

Answers the executive question: **"Where and how are we using AI tooling?"**

Register every internally-built AI agent as a Cortex entity with a named owner, a team, and links to its implementation. The **AI Agent Governance** scorecard ensures each agent is documented, classified by model and criticality tier, and periodically verified — giving leadership a live inventory of AI usage across the organization.

## Overview

```
  ┌──────────────────────────┐   ┌──────────────────────────┐   ┌──────────────────────────┐
  │         ai-agent         │   │         ai-agent         │   │         ai-agent         │
  │       code-review        │   │       audit-flags        │   │       jira-to-kb         │
  │                          │   │                          │   │                          │
  │  group: ai-model:        │   │  group: ai-model:        │   │  group: ai-model:        │
  │    claude-opus-4-6       │   │    claude-sonnet-4-6     │   │  claude-haiku-4-5-...    │
  │  group: tier1            │   │  group: tier3            │   │  group: tier3            │
  └──────────────────────────┘   └──────────────────────────┘   └──────────────────────────┘

  Filter by group "ai-model:claude-opus-4-6" → all agents on that model
  Filter by group "tier1"                    → all business-critical agents
  Scorecard "AI Agent Governance"            → Bronze / Silver / Gold across the catalog
```

AI model families and criticality tiers are Cortex **Groups**, not separate entity types. This keeps the classification lightweight and available anywhere groups appear — scorecard filters, catalog views, reports, and the Explore sidebar.

## What's Included

- **Entity type:** `ai-agent`
- **Scorecard:** `ai-agent-governance` — 6 rules across Bronze, Silver, and Gold levels
  - Bronze: has description · has a business owner (email) · owned by a team
  - Silver: tagged with an `ai-model:` group · tagged with a criticality tier (`tier-1` / `tier-2` / `tier-3`)
  - Gold: verified in the last 90 days
- **Sample entities:** 9 real agents from Cortex's own engineering org, drawn from the `cortexapps/brain-backend` skill library, intentionally spread across scoring levels so the scorecard tells a story out of the box:
  - **Silver:** `code-review`, `fix-issue`, `address-reviews`, `audit-flags`, `jira-to-kb`
  - **Bronze:** `simplify-test`, `incident-trends`, `search-troubleshooting-kb` (missing model + tier groups)
  - **Fails Bronze:** `release-to-sha` (no owner assigned)

## Installation

```
cortex solutions install -s ai-agents
```

## After Installing

**Replace the sample entities with your real agents**

The nine sample entities use `platform-engineering` as a placeholder team and `owner@example.com` as a placeholder business owner. For each real agent:

1. Create a new entity YAML (copy a sample as a template):
   ```
   cortex catalog create -f my-agent.yaml
   ```
2. Set the owning team and business owner:
   ```
   x-cortex-owners:
     - type: GROUP
       name: your-team-name
       provider: CORTEX
     - type: EMAIL
       email: real-owner@yourcompany.com
       description: business-owner
   ```
3. Tag it with the AI model and criticality tier:
   ```
   x-cortex-groups:
     - ai-model:claude-sonnet-4-6
     - tier-2
   ```
4. Point it at the agent's source code:
   ```
   x-cortex-git:
     github:
       repository: your-org/your-repo
       basepath: agents/my-agent
   ```

**Standard AI model groups**

Use these group tags consistently so filtering and reports work across agents:

| Model | Group tag |
|-------|-----------|
| Claude Opus 4.6 | `ai-model:claude-opus-4-6` |
| Claude Sonnet 4.6 | `ai-model:claude-sonnet-4-6` |
| Claude Haiku 4.5 | `ai-model:claude-haiku-4-5-20251001` |
| GPT-4o | `ai-model:gpt-4o` |
| GPT-4o mini | `ai-model:gpt-4o-mini` |
| Gemini 2.5 Pro | `ai-model:gemini-2-5-pro` |

As new models are introduced, follow the `ai-model:<provider>-<model-version>` naming convention so they are automatically picked up by the Silver scorecard rule — no rule changes needed.

**Linking to agent source code**

The sample entities use `x-cortex-git` with `basepath:` to scope Cortex's git features (commit history, code search) to just the agent's folder rather than the whole repository. Two variants depending on how the agent's code is organized:

*Folder-based agent (SKILL.md plus reference files, prompt directory, etc.):*

```
x-cortex-git:
  github:
    repository: your-org/your-repo
    basepath: agents/my-agent
```


**Reaching Gold**

The Gold rule checks that the agent has been verified within the last 90 days (`verifications().lastVerifiedAt() != null and verifications().lastVerifiedAt().fromNow() > duration("P-90D")`). Verify entities via the Cortex UI or API — none of the sample entities start at Gold by design. Wire a quarterly reminder or a GitHub Action on your agent directories to prompt re-verification when files change.

**Create an AI Agents Catalog in the UI**

Cortex Catalogs (the nav-level groupings) are UI-only today — no API or CLI support yet:

1. Go to [Catalogs](https://app.getcortexapp.com/admin/catalogs) → **New Catalog**
2. Entity type: `ai-agent`
3. Name it **AI Agents**

> Catalog creation will be automated once catalog API support is added to the CLI.

