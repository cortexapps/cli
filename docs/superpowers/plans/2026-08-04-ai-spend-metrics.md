# AI Usage & Spend Metrics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add custom-metrics import support to `cortex backup import` and build the `ai-spend` solution bundle with sample entity hierarchy, sample spend data, a sync script, and a GH Actions workflow.

**Architecture:** `backup.py` gains `_import_custom_metrics()` which reads one JSON file per metric key, groups entries by `entityTag`, and calls the per-entity bulk endpoint once per entity. The `solutions/ai-spend/` bundle is a self-contained directory that installs via `cortex backup import` and includes fictional teams/employees, 8 weeks of sample spend data, a Python sync script for the Anthropic Claude Enterprise Analytics API, and a weekly GH Actions workflow.

**Tech Stack:** Python 3.11+, Typer, existing `CortexClient`, `requests` (sync script only)

## Global Constraints

- Python 3.11+ syntax only (use `int | None` union syntax, not `Optional[int]`)
- Follow existing patterns in `backup.py` exactly: `_import_*` function signature, sequential import, `(type_name, imported_count, failed_list)` return tuple
- All solution files live under `cortexapps_cli/solutions/ai-spend/`
- Metric key: `ai-spend` (must be created in Cortex UI before importing data; the bulk API does NOT auto-create definitions)
- Bulk endpoint per entity: `POST /api/v1/eng-intel/custom-metrics/{key}/entity/{tagOrId}/bulk` with body `{"series": [{"timestamp": "...", "value": N}]}`
- File format for `custom-metrics/`: one `.json` file per metric key; entries are a flat list grouped by `entityTag` in the import code
- Email → tag mapping: `first.last@<EMAIL_DOMAIN>` → `employee-first-last`
- Sample data: 8 weekly timestamps, every Monday 2026-06-09 through 2026-07-28

---

## File Map

**Modified:**
- `cortexapps_cli/commands/backup.py` — add `_import_custom_metrics()`, wire into `import_tenant()`

**Created (solution static files):**
- `cortexapps_cli/solutions/ai-spend/entity-types/employee.json`
- `cortexapps_cli/solutions/ai-spend/entity-relationship-types/team-member.json`
- `cortexapps_cli/solutions/ai-spend/catalog/team-engineering.yaml`
- `cortexapps_cli/solutions/ai-spend/catalog/team-platform.yaml`
- `cortexapps_cli/solutions/ai-spend/catalog/team-frontend.yaml`
- `cortexapps_cli/solutions/ai-spend/catalog/team-data.yaml`
- `cortexapps_cli/solutions/ai-spend/catalog/employee-alice-chen.yaml`
- `cortexapps_cli/solutions/ai-spend/catalog/employee-bob-martinez.yaml`
- `cortexapps_cli/solutions/ai-spend/catalog/employee-carol-kim.yaml`
- `cortexapps_cli/solutions/ai-spend/catalog/employee-david-osei.yaml`
- `cortexapps_cli/solutions/ai-spend/catalog/employee-emma-johnson.yaml`
- `cortexapps_cli/solutions/ai-spend/custom-metrics/ai-spend.json`
- `cortexapps_cli/solutions/ai-spend/scripts/sync-claude-spend.py`
- `cortexapps_cli/solutions/ai-spend/.github/workflows/sync-claude-spend.yaml`
- `cortexapps_cli/solutions/ai-spend/README.md`

**Tests:**
- `tests/test_backup.py` — add `test_backup_import_custom_metrics_invalid_api_key`

---

## Task 1: Add `_import_custom_metrics()` to `backup.py`

**Files:**
- Modify: `cortexapps_cli/commands/backup.py`
- Test: `tests/test_backup.py`

**Interfaces:**
- Produces: `_import_custom_metrics(ctx, directory) -> tuple[str, int, list]` — returns `("custom-metrics", imported_count, [(file_path, error_type, error_msg), ...])`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_backup.py`:

```python
import json

def test_backup_import_custom_metrics_invalid_api_key(monkeypatch):
    """
    Test that backup import of custom-metrics fails cleanly with invalid API key.
    """
    monkeypatch.setenv("CORTEX_API_KEY", "invalidKey")

    with tempfile.TemporaryDirectory() as tmpdir:
        metrics_dir = os.path.join(tmpdir, "custom-metrics")
        os.makedirs(metrics_dir)

        metric_file = os.path.join(metrics_dir, "ai-spend.json")
        with open(metric_file, "w") as f:
            json.dump({
                "values": [
                    {
                        "entityTag": "employee-alice-chen",
                        "timestamp": "2026-07-28T00:00:00",
                        "value": 142.50
                    }
                ]
            }, f)

        result = cli(["backup", "import", "-d", tmpdir], return_type=ReturnType.RAW)
        assert result.exit_code != 0, (
            f"backup import should exit with non-zero code on failure, "
            f"got exit_code={result.exit_code}"
        )
```

- [ ] **Step 2: Run test to verify it fails**

```bash
poetry run pytest tests/test_backup.py::test_backup_import_custom_metrics_invalid_api_key -v
```

Expected: FAIL — `_import_custom_metrics` doesn't exist yet, but the test may actually pass vacuously (no `custom-metrics` dir handling means no failure). That's the signal: the function doesn't exist and no failure is triggered. We need to make it fail properly.

- [ ] **Step 3: Add `_import_custom_metrics` to `backup.py`**

Add this function after `_import_entity_relationships` (around line 472) and before `_has_relationships`:

```python
def _import_custom_metrics(ctx, directory):
    imported = 0
    failed = []
    if os.path.isdir(directory):
        print("Processing: " + directory)
        client = ctx.obj["client"]
        for filename in sorted(os.listdir(directory)):
            if not filename.endswith(".json"):
                continue
            file_path = os.path.join(directory, filename)
            if not os.path.isfile(file_path):
                continue
            metric_key = filename[:-5]  # strip .json
            try:
                print("   Importing: " + filename)
                with open(file_path) as f:
                    data = json.load(f)

                # Group flat values list by entityTag
                grouped = {}
                for entry in data.get("values", []):
                    tag = entry["entityTag"]
                    if tag not in grouped:
                        grouped[tag] = []
                    grouped[tag].append({
                        "timestamp": entry["timestamp"],
                        "value": entry["value"],
                    })

                # Call per-entity bulk endpoint once per entity
                for entity_tag, series in grouped.items():
                    client.post(
                        f"api/v1/eng-intel/custom-metrics/{metric_key}/entity/{entity_tag}/bulk",
                        data={"series": series},
                    )
                imported += 1
            except Exception as e:
                print(f"   Failed to import {filename}: {type(e).__name__} - {str(e)}")
                failed.append((file_path, type(e).__name__, str(e)))
    return ("custom-metrics", imported, failed)
```

- [ ] **Step 4: Wire into `import_tenant()`**

In `import_tenant()`, add the call after the `_import_entity_relationships` line (around line 764):

```python
    all_stats.append(_import_entity_relationships(ctx, directory + "/entity-relationships"))
    all_stats.append(_import_custom_metrics(ctx, directory + "/custom-metrics"))  # add this line
    all_stats.append(_import_plugins(ctx, directory + "/plugins"))
```

- [ ] **Step 5: Add retry hint to the failure reporting block**

In the `RETRY COMMANDS` section at the bottom of `import_tenant()`, add after the `elif import_type == "entity-relationships"` block:

```python
            elif import_type == "custom-metrics":
                print(f"# Manual retry needed for custom-metrics: {file_path}")
```

- [ ] **Step 6: Run test to verify it passes**

```bash
poetry run pytest tests/test_backup.py::test_backup_import_custom_metrics_invalid_api_key -v
```

Expected: PASS — the import now tries to call the API with an invalid key, fails, and exits non-zero.

- [ ] **Step 7: Run full backup test suite**

```bash
poetry run pytest tests/test_backup.py -v
```

Expected: all tests pass.

- [ ] **Step 8: Commit**

```bash
git add cortexapps_cli/commands/backup.py tests/test_backup.py
git commit -m "feat: add custom-metrics directory support to backup import"
```

---

## Task 2: Solution — Entity Types and Relationship Types

**Files:**
- Create: `cortexapps_cli/solutions/ai-spend/entity-types/employee.json`
- Create: `cortexapps_cli/solutions/ai-spend/entity-relationship-types/team-member.json`

**Interfaces:**
- Produces: `employee` entity type and `team-member` relationship type for use by all subsequent tasks

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p cortexapps_cli/solutions/ai-spend/entity-types
mkdir -p cortexapps_cli/solutions/ai-spend/entity-relationship-types
mkdir -p cortexapps_cli/solutions/ai-spend/catalog
mkdir -p cortexapps_cli/solutions/ai-spend/custom-metrics
mkdir -p cortexapps_cli/solutions/ai-spend/scripts
mkdir -p cortexapps_cli/solutions/ai-spend/.github/workflows
```

- [ ] **Step 2: Create `entity-types/employee.json`**

```json
{
  "type": "employee",
  "name": "Employee",
  "description": "A member of the organization. Used to track AI tool usage and spend per person.",
  "iconTag": "Cortex-builtin::Person",
  "schema": {"type": "object", "properties": {}}
}
```

- [ ] **Step 3: Create `entity-relationship-types/team-member.json`**

Single relationship type that allows both `team` and `employee` as destinations, enabling full hierarchy traversal from any team node.

```json
{
  "tag": "team-member",
  "name": "Team Member",
  "description": "Links a team to its direct members, which can be sub-teams or individual employees. Use this single relationship type to walk the full org hierarchy in the catalog.",
  "definitionLocation": "SOURCE",
  "isSingleSource": false,
  "isSingleDestination": false,
  "allowCycles": false,
  "sourcesFilter": {
    "include": true,
    "types": ["team"],
    "providers": []
  },
  "destinationsFilter": {
    "include": true,
    "types": ["team", "employee"],
    "providers": []
  },
  "inheritances": []
}
```

- [ ] **Step 4: Verify JSON is valid**

```bash
python3 -c "import json; json.load(open('cortexapps_cli/solutions/ai-spend/entity-types/employee.json'))"
python3 -c "import json; json.load(open('cortexapps_cli/solutions/ai-spend/entity-relationship-types/team-member.json'))"
```

Expected: no output (valid JSON).

- [ ] **Step 5: Commit**

```bash
git add cortexapps_cli/solutions/ai-spend/entity-types/ cortexapps_cli/solutions/ai-spend/entity-relationship-types/
git commit -m "add: ai-spend solution entity type and relationship type"
```

---

## Task 3: Solution — Catalog Entities

**Files:**
- Create: `cortexapps_cli/solutions/ai-spend/catalog/team-engineering.yaml`
- Create: `cortexapps_cli/solutions/ai-spend/catalog/team-platform.yaml`
- Create: `cortexapps_cli/solutions/ai-spend/catalog/team-frontend.yaml`
- Create: `cortexapps_cli/solutions/ai-spend/catalog/team-data.yaml`
- Create: `cortexapps_cli/solutions/ai-spend/catalog/employee-alice-chen.yaml`
- Create: `cortexapps_cli/solutions/ai-spend/catalog/employee-bob-martinez.yaml`
- Create: `cortexapps_cli/solutions/ai-spend/catalog/employee-carol-kim.yaml`
- Create: `cortexapps_cli/solutions/ai-spend/catalog/employee-david-osei.yaml`
- Create: `cortexapps_cli/solutions/ai-spend/catalog/employee-emma-johnson.yaml`

**Interfaces:**
- Consumes: `team-member` relationship type (Task 2)
- Produces: catalog entities with tags `team-engineering`, `team-platform`, `team-frontend`, `team-data`, `employee-alice-chen`, `employee-bob-martinez`, `employee-carol-kim`, `employee-david-osei`, `employee-emma-johnson`

Team hierarchy:
```
team-engineering
├── team-platform
│   ├── employee-alice-chen
│   └── employee-bob-martinez
├── team-frontend
│   ├── employee-carol-kim
│   └── employee-david-osei
└── team-data
    └── employee-emma-johnson
```

- [ ] **Step 1: Create `catalog/team-engineering.yaml`**

```yaml
openapi: "3.0.0"
info:
  title: Engineering
  x-cortex-tag: team-engineering
  x-cortex-type: team
  x-cortex-description: Top-level engineering organization
  x-cortex-definition: {}
  x-cortex-relationships:
    - type: team-member
      destinations:
        - tag: team-platform
        - tag: team-frontend
        - tag: team-data
```

- [ ] **Step 2: Create `catalog/team-platform.yaml`**

```yaml
openapi: "3.0.0"
info:
  title: Platform
  x-cortex-tag: team-platform
  x-cortex-type: team
  x-cortex-description: Platform engineering team
  x-cortex-definition: {}
  x-cortex-relationships:
    - type: team-member
      destinations:
        - tag: employee-alice-chen
        - tag: employee-bob-martinez
```

- [ ] **Step 3: Create `catalog/team-frontend.yaml`**

```yaml
openapi: "3.0.0"
info:
  title: Frontend
  x-cortex-tag: team-frontend
  x-cortex-type: team
  x-cortex-description: Frontend engineering team
  x-cortex-definition: {}
  x-cortex-relationships:
    - type: team-member
      destinations:
        - tag: employee-carol-kim
        - tag: employee-david-osei
```

- [ ] **Step 4: Create `catalog/team-data.yaml`**

```yaml
openapi: "3.0.0"
info:
  title: Data
  x-cortex-tag: team-data
  x-cortex-type: team
  x-cortex-description: Data engineering team
  x-cortex-definition: {}
  x-cortex-relationships:
    - type: team-member
      destinations:
        - tag: employee-emma-johnson
```

- [ ] **Step 5: Create `catalog/employee-alice-chen.yaml`**

```yaml
openapi: "3.0.0"
info:
  title: Alice Chen
  x-cortex-tag: employee-alice-chen
  x-cortex-type: employee
  x-cortex-description: Platform Engineer
  x-cortex-definition: {}
```

- [ ] **Step 6: Create `catalog/employee-bob-martinez.yaml`**

```yaml
openapi: "3.0.0"
info:
  title: Bob Martinez
  x-cortex-tag: employee-bob-martinez
  x-cortex-type: employee
  x-cortex-description: Platform Engineer
  x-cortex-definition: {}
```

- [ ] **Step 7: Create `catalog/employee-carol-kim.yaml`**

```yaml
openapi: "3.0.0"
info:
  title: Carol Kim
  x-cortex-tag: employee-carol-kim
  x-cortex-type: employee
  x-cortex-description: Frontend Engineer
  x-cortex-definition: {}
```

- [ ] **Step 8: Create `catalog/employee-david-osei.yaml`**

```yaml
openapi: "3.0.0"
info:
  title: David Osei
  x-cortex-tag: employee-david-osei
  x-cortex-type: employee
  x-cortex-description: Frontend Engineer
  x-cortex-definition: {}
```

- [ ] **Step 9: Create `catalog/employee-emma-johnson.yaml`**

```yaml
openapi: "3.0.0"
info:
  title: Emma Johnson
  x-cortex-tag: employee-emma-johnson
  x-cortex-type: employee
  x-cortex-description: Data Engineer
  x-cortex-definition: {}
```

- [ ] **Step 10: Verify YAML is valid**

```bash
python3 -c "
import yaml, glob
for f in glob.glob('cortexapps_cli/solutions/ai-spend/catalog/*.yaml'):
    yaml.safe_load(open(f))
    print('OK:', f)
"
```

Expected: `OK: ...` for all 9 files, no errors.

- [ ] **Step 11: Commit**

```bash
git add cortexapps_cli/solutions/ai-spend/catalog/
git commit -m "add: ai-spend solution catalog entities — teams and employees"
```

---

## Task 4: Solution — Sample Metric Data

**Files:**
- Create: `cortexapps_cli/solutions/ai-spend/custom-metrics/ai-spend.json`

**Interfaces:**
- Consumes: entity tags from Task 3
- Produces: `ai-spend.json` with 8 weekly data points per employee (format consumed by `_import_custom_metrics` from Task 1)

8 weekly timestamps (every Monday, 2026-06-09 through 2026-07-28):
`2026-06-09T00:00:00`, `2026-06-16T00:00:00`, `2026-06-23T00:00:00`, `2026-06-30T00:00:00`, `2026-07-07T00:00:00`, `2026-07-14T00:00:00`, `2026-07-21T00:00:00`, `2026-07-28T00:00:00`

- [ ] **Step 1: Create `custom-metrics/ai-spend.json`**

Values are in USD dollars rounded to 2 decimal places. Each employee has varied week-to-week values so charts look natural.

```json
{
  "values": [
    { "entityTag": "employee-alice-chen", "timestamp": "2026-06-09T00:00:00", "value": 162.70 },
    { "entityTag": "employee-alice-chen", "timestamp": "2026-06-16T00:00:00", "value": 195.40 },
    { "entityTag": "employee-alice-chen", "timestamp": "2026-06-23T00:00:00", "value": 134.60 },
    { "entityTag": "employee-alice-chen", "timestamp": "2026-06-30T00:00:00", "value": 178.90 },
    { "entityTag": "employee-alice-chen", "timestamp": "2026-07-07T00:00:00", "value": 156.20 },
    { "entityTag": "employee-alice-chen", "timestamp": "2026-07-14T00:00:00", "value": 203.80 },
    { "entityTag": "employee-alice-chen", "timestamp": "2026-07-21T00:00:00", "value": 142.50 },
    { "entityTag": "employee-alice-chen", "timestamp": "2026-07-28T00:00:00", "value": 187.30 },

    { "entityTag": "employee-bob-martinez", "timestamp": "2026-06-09T00:00:00", "value": 83.60 },
    { "entityTag": "employee-bob-martinez", "timestamp": "2026-06-16T00:00:00", "value": 118.20 },
    { "entityTag": "employee-bob-martinez", "timestamp": "2026-06-23T00:00:00", "value": 91.30 },
    { "entityTag": "employee-bob-martinez", "timestamp": "2026-06-30T00:00:00", "value": 103.50 },
    { "entityTag": "employee-bob-martinez", "timestamp": "2026-07-07T00:00:00", "value": 76.80 },
    { "entityTag": "employee-bob-martinez", "timestamp": "2026-07-14T00:00:00", "value": 112.60 },
    { "entityTag": "employee-bob-martinez", "timestamp": "2026-07-21T00:00:00", "value": 87.20 },
    { "entityTag": "employee-bob-martinez", "timestamp": "2026-07-28T00:00:00", "value": 98.40 },

    { "entityTag": "employee-carol-kim", "timestamp": "2026-06-09T00:00:00", "value": 161.40 },
    { "entityTag": "employee-carol-kim", "timestamp": "2026-06-16T00:00:00", "value": 149.80 },
    { "entityTag": "employee-carol-kim", "timestamp": "2026-06-23T00:00:00", "value": 138.20 },
    { "entityTag": "employee-carol-kim", "timestamp": "2026-06-30T00:00:00", "value": 172.60 },
    { "entityTag": "employee-carol-kim", "timestamp": "2026-07-07T00:00:00", "value": 155.30 },
    { "entityTag": "employee-carol-kim", "timestamp": "2026-07-14T00:00:00", "value": 128.40 },
    { "entityTag": "employee-carol-kim", "timestamp": "2026-07-21T00:00:00", "value": 167.90 },
    { "entityTag": "employee-carol-kim", "timestamp": "2026-07-28T00:00:00", "value": 143.70 },

    { "entityTag": "employee-david-osei", "timestamp": "2026-06-09T00:00:00", "value": 63.70 },
    { "entityTag": "employee-david-osei", "timestamp": "2026-06-16T00:00:00", "value": 89.40 },
    { "entityTag": "employee-david-osei", "timestamp": "2026-06-23T00:00:00", "value": 58.90 },
    { "entityTag": "employee-david-osei", "timestamp": "2026-06-30T00:00:00", "value": 71.60 },
    { "entityTag": "employee-david-osei", "timestamp": "2026-07-07T00:00:00", "value": 82.10 },
    { "entityTag": "employee-david-osei", "timestamp": "2026-07-14T00:00:00", "value": 54.20 },
    { "entityTag": "employee-david-osei", "timestamp": "2026-07-21T00:00:00", "value": 78.40 },
    { "entityTag": "employee-david-osei", "timestamp": "2026-07-28T00:00:00", "value": 65.30 },

    { "entityTag": "employee-emma-johnson", "timestamp": "2026-06-09T00:00:00", "value": 201.50 },
    { "entityTag": "employee-emma-johnson", "timestamp": "2026-06-16T00:00:00", "value": 193.40 },
    { "entityTag": "employee-emma-johnson", "timestamp": "2026-06-23T00:00:00", "value": 219.80 },
    { "entityTag": "employee-emma-johnson", "timestamp": "2026-06-30T00:00:00", "value": 208.60 },
    { "entityTag": "employee-emma-johnson", "timestamp": "2026-07-07T00:00:00", "value": 187.30 },
    { "entityTag": "employee-emma-johnson", "timestamp": "2026-07-14T00:00:00", "value": 225.10 },
    { "entityTag": "employee-emma-johnson", "timestamp": "2026-07-21T00:00:00", "value": 198.70 },
    { "entityTag": "employee-emma-johnson", "timestamp": "2026-07-28T00:00:00", "value": 212.40 }
  ]
}
```

- [ ] **Step 2: Verify JSON is valid and has the right count**

```bash
python3 -c "
import json
data = json.load(open('cortexapps_cli/solutions/ai-spend/custom-metrics/ai-spend.json'))
values = data['values']
print(f'Total entries: {len(values)}')  # expect 40 (5 employees × 8 weeks)
tags = set(v['entityTag'] for v in values)
print(f'Unique entities: {sorted(tags)}')
from collections import Counter
counts = Counter(v['entityTag'] for v in values)
print(f'Points per entity: {dict(counts)}')
"
```

Expected:
```
Total entries: 40
Unique entities: ['employee-alice-chen', 'employee-bob-martinez', 'employee-carol-kim', 'employee-david-osei', 'employee-emma-johnson']
Points per entity: {'employee-alice-chen': 8, 'employee-bob-martinez': 8, 'employee-carol-kim': 8, 'employee-david-osei': 8, 'employee-emma-johnson': 8}
```

- [ ] **Step 3: Commit**

```bash
git add cortexapps_cli/solutions/ai-spend/custom-metrics/
git commit -m "add: ai-spend solution sample metric data (8 weeks)"
```

---

## Task 5: Solution — Sync Script

**Files:**
- Create: `cortexapps_cli/solutions/ai-spend/scripts/sync-claude-spend.py`

**Interfaces:**
- Produces: standalone Python script, callable as `python sync-claude-spend.py [--start YYYY-MM-DD] [--end YYYY-MM-DD]`
- Env vars consumed: `ANTHROPIC_ANALYTICS_KEY`, `CORTEX_API_KEY`, `CORTEX_BASE_URL`, `EMAIL_DOMAIN`

**Note on the Anthropic endpoint:** The Claude Enterprise Analytics API costs endpoint is `GET /v1/organizations/analytics/costs`. This is based on the documented API structure; verify the exact parameters once an Analytics API key is available. The response structure follows the same pattern as the Claude Code Analytics API: `{"data": [...], "has_more": bool, "next_page": str|null}`. Cost amounts are decimal strings in cents.

- [ ] **Step 1: Create `scripts/sync-claude-spend.py`**

```python
#!/usr/bin/env python3
"""
sync-claude-spend.py

Pulls per-user spend from the Anthropic Claude Enterprise Analytics API
and pushes weekly cost data to Cortex as custom metric data points.

Requirements:
    pip install requests

Environment variables:
    ANTHROPIC_ANALYTICS_KEY  Required. Analytics API key from claude.ai org settings.
                             Only the primary owner can create this key at:
                             claude.ai > Organization settings > API
    CORTEX_API_KEY           Required. Cortex API key.
    CORTEX_BASE_URL          Optional. Defaults to https://api.getcortexapp.com
    EMAIL_DOMAIN             Optional. Domain to strip from emails. Defaults to cortex.io

Usage:
    python sync-claude-spend.py
    python sync-claude-spend.py --start 2026-07-21 --end 2026-07-28

Notes:
    - Users who authenticate via API key (not Enterprise OAuth) will show $0 spend
      in the Analytics API and are skipped automatically.
    - The Cortex custom metric definition for "ai-spend" must already exist in your
      Cortex instance before running this script. Create it in the Cortex UI under
      Eng Intel > Custom Metrics.
"""

import argparse
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import requests

ANTHROPIC_BASE_URL = "https://api.anthropic.com"
ANTHROPIC_VERSION = "2023-06-01"
CORTEX_METRIC_KEY = "ai-spend"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Sync Claude Enterprise spend to Cortex custom metrics"
    )
    parser.add_argument(
        "--start",
        help="Start date YYYY-MM-DD (default: 7 days ago)",
        default=None,
    )
    parser.add_argument(
        "--end",
        help="End date YYYY-MM-DD (default: yesterday)",
        default=None,
    )
    return parser.parse_args()


def get_env(key, required=True, default=None):
    value = os.environ.get(key, default)
    if required and not value:
        print(f"ERROR: Environment variable {key} is required", file=sys.stderr)
        sys.exit(1)
    return value


def email_to_entity_tag(email, domain):
    """
    Maps first.last@domain -> employee-first-last.
    Returns None if email doesn't match the expected domain or format.
    """
    if not email.endswith(f"@{domain}"):
        return None
    local = email.split("@")[0]
    parts = local.split(".")
    if len(parts) != 2:
        return None
    return f"employee-{parts[0]}-{parts[1]}"


def fetch_claude_spend(analytics_key, start_date, end_date):
    """
    Fetch per-user cost data from the Claude Enterprise Analytics API.

    Returns list of dicts: {"email": str, "cost_dollars": float}
    Only includes records where cost > 0.

    Endpoint: GET /v1/organizations/analytics/costs
    Verify exact query parameters once an Analytics API key is available.
    """
    headers = {
        "x-api-key": analytics_key,
        "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json",
    }

    results = []
    cursor = None

    while True:
        params = {
            "starting_at": start_date,
            "ending_at": end_date,
        }
        if cursor:
            params["page"] = cursor

        url = f"{ANTHROPIC_BASE_URL}/v1/organizations/analytics/costs"
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        body = response.json()

        for record in body.get("data", []):
            actor = record.get("actor", {})
            email = actor.get("email_address")
            if not email:
                continue

            # Cost is returned as a decimal string in cents (e.g. "14250.000000" = $142.50)
            cost_str = record.get("cost", "0")
            try:
                cost_dollars = float(cost_str) / 100
            except (ValueError, TypeError):
                cost_dollars = 0.0

            if cost_dollars > 0:
                results.append({"email": email, "cost_dollars": cost_dollars})

        if not body.get("has_more"):
            break
        cursor = body.get("next_page")

    return results


def push_to_cortex(cortex_api_key, cortex_base_url, entity_tag, series):
    """
    Push spend data points for a single entity to Cortex.

    series: list of {"timestamp": str, "value": float}
    Calls: POST /api/v1/eng-intel/custom-metrics/{key}/entity/{tag}/bulk
    """
    url = (
        f"{cortex_base_url}/api/v1/eng-intel/custom-metrics"
        f"/{CORTEX_METRIC_KEY}/entity/{entity_tag}/bulk"
    )
    headers = {
        "Authorization": f"Bearer {cortex_api_key}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        url, headers=headers, json={"series": series}, timeout=30
    )
    response.raise_for_status()


def main():
    args = parse_args()

    analytics_key = get_env("ANTHROPIC_ANALYTICS_KEY")
    cortex_api_key = get_env("CORTEX_API_KEY")
    cortex_base_url = get_env(
        "CORTEX_BASE_URL", required=False, default="https://api.getcortexapp.com"
    )
    email_domain = get_env("EMAIL_DOMAIN", required=False, default="cortex.io")

    today = datetime.now(timezone.utc).date()
    start_date = args.start or str(today - timedelta(days=7))
    end_date = args.end or str(today - timedelta(days=1))
    # Use end_date as the metric timestamp (represents the week ending on this date)
    timestamp = f"{end_date}T00:00:00"

    print(f"Fetching Claude spend from {start_date} to {end_date}...")

    try:
        spend_records = fetch_claude_spend(analytics_key, start_date, end_date)
    except requests.HTTPError as e:
        print(f"ERROR: Failed to fetch spend data from Anthropic: {e}", file=sys.stderr)
        sys.exit(1)

    # Map emails to entity tags; collect skips
    entity_series = defaultdict(list)
    skipped = []

    for record in spend_records:
        email = record["email"]
        entity_tag = email_to_entity_tag(email, email_domain)
        if not entity_tag:
            skipped.append((email, "domain mismatch or unexpected format"))
            continue
        entity_series[entity_tag].append({
            "timestamp": timestamp,
            "value": round(record["cost_dollars"], 2),
        })

    if not entity_series:
        print("No spend records matched — nothing to push.")
    else:
        print(f"Pushing spend for {len(entity_series)} employee(s) to Cortex...")
        push_errors = []
        for entity_tag, series in sorted(entity_series.items()):
            try:
                push_to_cortex(cortex_api_key, cortex_base_url, entity_tag, series)
                print(f"  OK: {entity_tag}")
            except requests.HTTPError as e:
                print(f"  FAIL: {entity_tag}: {e}", file=sys.stderr)
                push_errors.append(entity_tag)

        if push_errors:
            print(f"\nERROR: Failed to push {len(push_errors)} entities.", file=sys.stderr)
            sys.exit(1)

    print(f"\nSummary:")
    print(f"  Updated: {len(entity_series)} employee(s)")
    print(f"  Skipped: {len(skipped)}")
    for email, reason in skipped:
        print(f"    - {email}: {reason}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify the script is syntactically valid**

```bash
python3 -m py_compile cortexapps_cli/solutions/ai-spend/scripts/sync-claude-spend.py && echo "OK"
```

Expected: `OK`

- [ ] **Step 3: Verify help output**

```bash
python3 cortexapps_cli/solutions/ai-spend/scripts/sync-claude-spend.py --help
```

Expected: usage text showing `--start` and `--end` options, no errors.

- [ ] **Step 4: Commit**

```bash
git add cortexapps_cli/solutions/ai-spend/scripts/
git commit -m "add: ai-spend solution sync script for Claude Enterprise Analytics API"
```

---

## Task 6: Solution — GH Actions Workflow and README

**Files:**
- Create: `cortexapps_cli/solutions/ai-spend/.github/workflows/sync-claude-spend.yaml`
- Create: `cortexapps_cli/solutions/ai-spend/README.md`

**Interfaces:**
- Consumes: `scripts/sync-claude-spend.py` (Task 5)

- [ ] **Step 1: Create `.github/workflows/sync-claude-spend.yaml`**

```yaml
name: Sync Claude AI Spend to Cortex

on:
  schedule:
    - cron: "0 6 * * 1"  # Every Monday at 06:00 UTC
  workflow_dispatch:       # Allow manual runs from the Actions tab

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install requests

      - name: Sync Claude spend to Cortex
        env:
          ANTHROPIC_ANALYTICS_KEY: ${{ secrets.ANTHROPIC_ANALYTICS_KEY }}
          CORTEX_API_KEY: ${{ secrets.CORTEX_API_KEY }}
        run: python scripts/sync-claude-spend.py
```

- [ ] **Step 2: Create `README.md`**

```markdown
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
cortex backup import -d /path/to/solutions/ai-spend
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
```

- [ ] **Step 3: Verify YAML workflow is valid**

```bash
python3 -c "import yaml; yaml.safe_load(open('cortexapps_cli/solutions/ai-spend/.github/workflows/sync-claude-spend.yaml')); print('OK')"
```

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add cortexapps_cli/solutions/ai-spend/.github/ cortexapps_cli/solutions/ai-spend/README.md
git commit -m "add: ai-spend solution GH Actions workflow and README"
```

---

## Self-Review

### Spec coverage

| Spec requirement | Task |
|---|---|
| `_import_custom_metrics()` in `backup.py` | Task 1 |
| Called after entity-relationships in `import_tenant()` | Task 1 |
| Filename stem = metric key | Task 1 |
| Groups by entityTag, calls per-entity bulk endpoint | Task 1 |
| Test with invalid API key | Task 1 |
| `employee` entity type | Task 2 |
| `team-member` relationship type (source=team, dest=team\|employee) | Task 2 |
| 4 teams with hierarchy | Task 3 |
| 5 employees across teams | Task 3 |
| `x-cortex-relationships` wired in team YAMLs | Task 3 |
| `custom-metrics/ai-spend.json` with 8 weeks of data | Task 4 |
| 5 employees × 8 weekly points | Task 4 |
| `sync-claude-spend.py` with Claude Enterprise Analytics API | Task 5 |
| Email → entity tag mapping | Task 5 |
| Skip $0 spend users | Task 5 |
| `ANTHROPIC_ANALYTICS_KEY`, `CORTEX_API_KEY`, `CORTEX_BASE_URL`, `EMAIL_DOMAIN` env vars | Task 5 |
| Weekly GH Actions schedule (Monday 06:00 UTC) | Task 6 |
| `workflow_dispatch` for manual runs | Task 6 |
| README with install instructions | Task 6 |

All spec requirements covered. No gaps found.

### Corrections from brainstorming

- Design spec said "cross-entity bulk endpoint (no entity tag in path)" — the Cortex API has no such endpoint. Implementation correctly uses the per-entity bulk endpoint `POST .../entity/{tag}/bulk` with grouping by `entityTag` in the import code. File format is unchanged.
