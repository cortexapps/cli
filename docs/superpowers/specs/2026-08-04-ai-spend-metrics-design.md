# AI Usage & Spend Metrics — Design Spec

**Date:** 2026-08-04
**Linear:** CX-2

---

## Overview

Track per-employee Claude AI spend in Cortex using custom metrics. Employees are catalog entities linked to teams via a single relationship type that supports a full team hierarchy. Spend data is pushed weekly via a script that polls the Anthropic Claude Enterprise Analytics API.

This feature has two parts:
1. **CLI change** — add `custom-metrics` directory support to `cortex backup import`
2. **New solution** — `solutions/ai-spend/` with entity types, sample entities, sample metric data, sync script, and GH Actions workflow

---

## Part 1: CLI Change — `backup import` Custom Metrics Support

### What changes

`cortexapps_cli/commands/backup.py` gains a new `_import_custom_metrics(ctx, directory)` function, following the exact pattern of every other `_import_*` function in that file.

### File format

One JSON file per metric key. Filename stem = metric key. Example: `custom-metrics/ai-spend.json`

```json
{
  "values": [
    { "entityTag": "employee-alice-chen", "timestamp": "2026-07-28T00:00:00", "value": 142.50 },
    { "entityTag": "employee-bob-martinez", "timestamp": "2026-07-28T00:00:00", "value": 87.20 }
  ]
}
```

### API call

`POST /api/v1/eng-intel/custom-metrics/{key}/entity/bulk` (cross-entity bulk endpoint — no entity tag in path).

### Import behavior

- Reads every `*.json` file in the `custom-metrics/` directory
- Uses filename stem as the metric key
- Imports sequentially (files are independent; no ordering constraint; parallelism adds no benefit)
- Called from `import_tenant()` after `entity-relationships` so entities exist before metrics land
- Follows existing error handling and summary reporting patterns

### What does NOT change

- No export support — custom metrics are time-series data from external sources; backup export of them has no value
- `custom-metrics` is not added to `backupTypes` (the set used to validate the `--export-types` flag — import doesn't use it)
- No new CLI flags or commands

---

## Part 2: Solution — `solutions/ai-spend/`

### Directory structure

```
solutions/ai-spend/
├── README.md
├── entity-types/
│   └── employee.json
├── entity-relationship-types/
│   └── team-member.json
├── catalog/
│   ├── team-engineering.yaml
│   ├── team-platform.yaml
│   ├── team-frontend.yaml
│   ├── team-data.yaml
│   ├── employee-alice-chen.yaml
│   ├── employee-bob-martinez.yaml
│   ├── employee-carol-kim.yaml
│   ├── employee-david-osei.yaml
│   └── employee-emma-johnson.yaml
├── custom-metrics/
│   └── ai-spend.json
├── scripts/
│   └── sync-claude-spend.py
└── .github/
    └── workflows/
        └── sync-claude-spend.yaml
```

### Entity type: `employee`

Custom entity type. Minimal schema — just enough to register the type. Icon: a person/user icon from Cortex builtins.

### Entity relationship type: `team-member`

- Source: `team` (built-in)
- Destination: `team` or `employee` (single type, supports both)
- This single type allows walking the full hierarchy from any team node in the catalog

### Team hierarchy (sample data)

```
team-engineering          (top-level)
├── team-platform
│   ├── employee-alice-chen
│   └── employee-bob-martinez
├── team-frontend
│   ├── employee-carol-kim
│   └── employee-david-osei
└── team-data
    └── employee-emma-johnson
```

Teams are wired via `x-cortex-relationships` in the team catalog YAMLs using the `team-member` relationship type.

### Sample metric data: `custom-metrics/ai-spend.json`

- Metric key: `ai-spend`
- 8 weekly data points per employee, backdated from 2026-08-04
- Timestamps: every Monday for the past 8 weeks (2026-06-09 through 2026-07-28)
- Realistic-looking fictional dollar values (range: $40–$220/week per employee), varied week-to-week so charts look natural

### Sync script: `scripts/sync-claude-spend.py`

**Purpose:** Pull per-user spend from the Anthropic Claude Enterprise Analytics API and push to Cortex as custom metric data points.

**Auth context:** Cortex uses Claude Enterprise (claude.ai), not the API console. Analytics API keys are created at `claude.ai > Organization settings > API` by the primary owner. The key goes in `x-api-key` on calls to `https://api.anthropic.com/v1/organizations/analytics/`.

**Email → entity tag mapping:**

```
first.last@<domain> → employee-first-last
```

Domain is configurable via `EMAIL_DOMAIN` env var (default: `cortex.io`).

**Script behavior:**
1. Compute date range: past 7 days (configurable via `--start` / `--end` flags)
2. Call Claude Enterprise Analytics API cost/usage endpoint, paginate until done
3. Filter to records where `cost > 0` (skip $0.00 users who authenticate via API key rather than Enterprise OAuth — their costs appear in separate API billing)
4. Map email to entity tag; skip records where email domain doesn't match or transform fails
5. Build `ai-spend` bulk payload and POST to Cortex custom metrics API
6. Print summary: N users updated, N skipped (with reasons)

**Environment variables:**

| Var | Required | Default | Description |
|-----|----------|---------|-------------|
| `ANTHROPIC_ANALYTICS_KEY` | Yes | — | Analytics API key from claude.ai org settings |
| `CORTEX_API_KEY` | Yes | — | Cortex API key |
| `CORTEX_BASE_URL` | No | `https://api.getcortexapp.com` | Cortex instance URL |
| `EMAIL_DOMAIN` | No | `cortex.io` | Domain to strip when mapping emails to entity tags |

**Dependencies:** `requests` (no Anthropic SDK needed — Analytics API is plain REST)

### GH Actions workflow: `.github/workflows/sync-claude-spend.yaml`

- **Trigger:** `schedule` — weekly, every Monday at 06:00 UTC; plus `workflow_dispatch` for manual runs
- **Secrets:** `ANTHROPIC_ANALYTICS_KEY`, `CORTEX_API_KEY`
- **Steps:** checkout → `pip install requests` → run `scripts/sync-claude-spend.py`
- **Failure behavior:** non-zero exit fails the workflow so GH sends the standard failure notification

---

## Data Flow

```
Claude Enterprise Analytics API
        │
        │  GET /v1/organizations/analytics/costs
        │  (weekly, per-user spend)
        ▼
sync-claude-spend.py
        │
        │  email → employee-first-last
        │  POST /api/v1/eng-intel/custom-metrics/ai-spend/entity/bulk
        ▼
Cortex Custom Metrics
        │
        │  displayed on employee entity page
        │  aggregatable up the team hierarchy
        ▼
Cortex Catalog (team-engineering → team-platform → employee-alice-chen)
```

---

## What's Not In Scope

- Export of custom metrics (no backup export support)
- Supporting the Anthropic API console Usage & Cost API (covers API-key users with $0 enterprise spend) — deferred
- Importing custom metric *definitions* (metric key must already exist in Cortex) — the solution installs sample data but customers need to create their `ai-spend` metric definition manually or via a separate step
- Per-team spend rollup in Cortex — this is handled by Cortex natively once entity relationships are in place

---

## Open Questions

- **Custom metric definition creation:** does `backup import` need to create the metric definition (`ai-spend`) before pushing data, or does the bulk endpoint auto-create it? Needs verification against the API.
- **Analytics API endpoint:** exact endpoint path for Claude Enterprise cost-per-user report needs confirmation once an Analytics API key is available (primary owner is on sabbatical for ~8 weeks; using sample data until then).
