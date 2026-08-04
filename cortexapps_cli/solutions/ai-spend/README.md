---
name: AI Spend
description: Track per-employee Claude AI spend in Cortex using custom metrics, with a full team hierarchy for rollup visibility.
---

# AI Spend

Answers the question: **"How much are we spending on Claude AI, and who's spending it?"**

Register every employee as a Cortex entity linked to their team, push weekly Claude spend as a custom metric, and roll costs up the org hierarchy — from individual → sub-team → top-level engineering.

## Overview

```
  team-engineering
  ├── team-platform
  │   ├── employee-alice-chen        ai-spend: $187/wk
  │   └── employee-bob-martinez      ai-spend:  $98/wk
  ├── team-frontend
  │   ├── employee-carol-kim         ai-spend: $144/wk
  │   └── employee-david-osei        ai-spend:  $65/wk
  └── team-data
      └── employee-emma-johnson      ai-spend: $212/wk

  Custom metric "ai-spend" on each employee entity
  Team rollup visible via entity relationships in Cortex catalog
```

## What's Included

| Resource | Tag / Key |
|---|---|
| Entity type | `employee` |
| Relationship type | `team-member` (team → team\|employee) |
| Teams | `team-engineering`, `team-platform`, `team-frontend`, `team-data` |
| Employees | `employee-alice-chen`, `employee-bob-martinez`, `employee-carol-kim`, `employee-david-osei`, `employee-emma-johnson` |
| Custom metric sample data | `ai-spend` (8 weeks, fictional) |
| Sync script | `scripts/sync-claude-spend.py` |
| GH Actions workflow | `.github/workflows/sync-claude-spend.yaml` |

## Prerequisites

Before installing, create the `ai-spend` custom metric definition in your Cortex instance:
**Eng Intel → Custom Metrics → New Metric**, key: `ai-spend`.

## Installation

```
cortex solutions install -s ai-spend
```

## After Installing

**Set up live Claude spend sync**

The sample entities include fictional spend data. To push real data from your Anthropic Claude Enterprise account weekly:

1. **Get an Analytics API key:**
   - Sign in to claude.ai as the **primary owner** of your organization
   - Go to **Organization settings → API**
   - Enable public API access and create an Analytics API key
   - (Only the primary owner can create this key — admin role is not sufficient)

2. **Add secrets to your GitHub repo:**
   - `ANTHROPIC_ANALYTICS_KEY` — the Analytics API key from step 1
   - `CORTEX_API_KEY` — your Cortex API key

3. **Copy the workflow** to your repo's `.github/workflows/` directory:
   ```bash
   cp .github/workflows/sync-claude-spend.yaml <your-repo>/.github/workflows/
   ```

4. **Copy the script** to your repo's `scripts/` directory:
   ```bash
   cp scripts/sync-claude-spend.py <your-repo>/scripts/
   ```

The workflow runs every Monday at 06:00 UTC and can be triggered manually from the GitHub Actions tab.

**Customize the email domain**

The sync script maps `first.last@cortex.io` → `employee-first-last`. Set `EMAIL_DOMAIN` in the workflow env to match your company's domain:

```yaml
env:
  EMAIL_DOMAIN: yourcompany.com
```

**Add your real employees**

The sample entities are fictional. Add your real employees as catalog entities with `x-cortex-type: employee` and tag them `employee-<first>-<last>` to match the email mapping.

**Notes**

- Users who authenticate Claude Code with a personal API key (not Enterprise OAuth) show $0 spend in the Analytics API and are skipped automatically.
- Cost data may take up to 24 hours to appear; dates at least 30 days old are considered final for billing purposes.
