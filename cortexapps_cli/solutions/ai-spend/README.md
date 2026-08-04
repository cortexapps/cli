# AI Spend Solution

Track per-employee Claude AI spend in Cortex using custom metrics, with a full team
hierarchy for rollup visibility.

## What This Installs

| Resource | Tag / Key |
|---|---|
| Entity type | `employee` |
| Relationship type | `team-member` (team → team\|employee) |
| Teams | `team-engineering`, `team-platform`, `team-frontend`, `team-data` |
| Employees | `employee-alice-chen`, `employee-bob-martinez`, `employee-carol-kim`, `employee-david-osei`, `employee-emma-johnson` |
| Custom metric sample data | `ai-spend` (8 weeks, fictional) |

## Prerequisites

Before installing, create the `ai-spend` custom metric definition in your Cortex
instance: **Eng Intel → Custom Metrics → New Metric**, key: `ai-spend`.

## Install

```bash
cortex solutions install -s ai-spend
```

## Live Sync Setup

To push real Claude spend data weekly:

1. **Get an Analytics API key:**
   - Sign in to claude.ai as the **primary owner** of your organization
   - Go to **Organization settings → API**
   - Enable public API access and create an Analytics API key

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

The workflow runs every Monday at 06:00 UTC and can be triggered manually from
the GitHub Actions tab.

## Email → Entity Tag Mapping

The sync script maps `first.last@yourdomain.com` → `employee-first-last`.

Set `EMAIL_DOMAIN` in the workflow env if your domain isn't `cortex.io`:

```yaml
env:
  EMAIL_DOMAIN: yourcompany.com
```

## Notes

- Users who authenticate Claude Code with a personal API key (not Enterprise OAuth)
  will show $0 spend in the Analytics API and are skipped automatically.
- Cost data may take up to 24 hours to appear; query dates at least 30 days old
  are considered final for billing purposes.
