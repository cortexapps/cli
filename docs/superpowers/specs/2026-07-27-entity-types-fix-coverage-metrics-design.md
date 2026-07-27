# Design: entity-types update fix + pytest coverage metrics

**Date:** 2026-07-27

## Overview

Two changes bundled together:
1. Fix a crashing bug in `cortex entity-types update`
2. Post pytest coverage data as custom metrics/metadata to the `cli` entity in Cortex production daily

---

## Part 1: entity-types update bug fix

### Problem

`entity_types.update()` calls `client.update()`, which does not exist on `CortexClient`. Every invocation crashes with `AttributeError`. Additionally, the function captures the response in `r` but never prints it.

### Fix

**`cortexapps_cli/commands/entity_types.py`**

- Replace `client.update(...)` with `client.put(...)`
- Add `_print: CommandOptions._print = True` parameter
- Add `if _print: print_output_with_context(ctx, r)` after the call

**`tests/test_entity_types.py`**

Harden the existing `update` call to assert success:
```python
response = cli(["entity-types", "update", "-t", "cli-test", "-f", "data/run-time/entity-type-update.json"], return_type=ReturnType.RAW)
assert response.exit_code == 0
```

---

## Part 2: pytest coverage metrics

### Goal

After the daily test run, post two pieces of coverage data to the `cli` entity in Cortex production:
1. **Total coverage percentage** as a custom metric (`code-coverage-pct`)
2. **Per-file coverage summary** as custom metadata (`pytest-coverage`)

### Changes

#### Justfile: `test-all` recipe

Add `--cov-report json:coverage.json` alongside the existing `--cov-report term-missing`. Purely additive — terminal output is unchanged.

#### New file: `scripts/post_coverage.py`

Reads `coverage.json` (written by pytest-cov) and fires two cortex CLI calls:

1. `cortex custom-metrics add -t cli -k code-coverage-pct -v <total_pct>`
2. Writes a temp JSON file and calls `cortex custom-data add -t cli -k pytest-coverage -f <tempfile>`

The custom metadata value shape:
```json
{
  "total_pct": 83.3,
  "files": [
    { "file": "cortexapps_cli/commands/catalog.py", "lines_tested": 45, "lines_missing": 15, "pct": 75.0 }
  ]
}
```

The script uses `subprocess` to call the cortex CLI (already installed in the CI environment). It reads `CORTEX_API_KEY` from the environment — no new secrets required.

#### `.github/workflows/test-daily.yml`

Add one step after `just test-all`:
```yaml
- name: Post coverage metrics to Cortex
  run: python scripts/post_coverage.py
```

The `CORTEX_API_KEY` env var is already available in this workflow.

### What is NOT changed

- `test-pr.yml` — no changes; metrics are daily only
- `publish.yml` — no changes
- Terminal coverage output — unchanged
- No new GitHub secrets required

---

## Commit strategy

Single feature branch. Two logical commits:
1. `fix: entity-types update calls nonexistent client method`
2. `feat: post pytest coverage metrics to Cortex daily`

Minor version bump on release (due to `feat:` commit).
