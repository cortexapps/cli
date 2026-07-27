# entity-types fix + pytest coverage metrics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix a crashing bug in `cortex entity-types update` and post pytest coverage data as custom metrics/metadata to the `cli` entity in Cortex production after every daily test run.

**Architecture:** Two independent commits on one feature branch. The bug fix uses TDD — harden the test first to make it fail, then fix the code. The coverage feature adds JSON report output to the existing test recipe, a new Python script that posts two Cortex API calls, and one new step in `test-daily.yml`.

**Tech Stack:** Python 3.11+, Typer, pytest-cov (coverage JSON output), subprocess, cortex CLI (`custom-metrics add`, `custom-data add`)

## Global Constraints

- Python 3.11+ syntax only
- Follow existing command patterns in `cortexapps_cli/commands/` (see `entity_relationship_types.py` as the reference sibling)
- All CLI commands must accept `_print: CommandOptions._print = True` and call `print_output_with_context` when `_print` is true
- Commit prefix `fix:` for the bug fix, `feat:` for the coverage feature
- Do not modify `test-pr.yml` or `publish.yml`
- `coverage.json` is already in `.gitignore` — do not add it to git

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `cortexapps_cli/commands/entity_types.py` | Modify lines 99–111 | Fix `update()` to call `client.put()` and print output |
| `tests/test_entity_types.py` | Modify line 22 | Assert `exit_code == 0` on update call |
| `Justfile` | Modify `test-all` recipe | Add `--cov-report json:coverage.json` |
| `scripts/post_coverage.py` | Create | Read coverage.json, post metric + custom data to Cortex |
| `.github/workflows/test-daily.yml` | Modify | Add step to run `scripts/post_coverage.py` after tests |

---

## Task 1: Fix entity-types update (TDD)

**Files:**
- Modify: `tests/test_entity_types.py:22`
- Modify: `cortexapps_cli/commands/entity_types.py:99-111`

**Interfaces:**
- Produces: `entity_types.update(ctx, file_input, entity_type, _print)` — calls `client.put("api/v1/catalog/definitions/{entity_type}", data=data)`, calls `print_output_with_context(ctx, r)` when `_print` is true

- [ ] **Step 1: Create the feature branch**

```bash
git checkout -b 227-entity-types-fix-coverage-metrics
```

- [ ] **Step 2: Harden the test to make it fail**

Open `tests/test_entity_types.py`. Replace line 22:

```python
# BEFORE:
cli(["entity-types", "update", "-t", "cli-test", "-f", "data/run-time/entity-type-update.json"])

# AFTER:
response = cli(["entity-types", "update", "-t", "cli-test", "-f", "data/run-time/entity-type-update.json"], return_type=ReturnType.RAW)
assert response.exit_code == 0
```

- [ ] **Step 3: Run the test to confirm it fails**

```bash
just test tests/test_entity_types.py
```

Expected: `FAILED tests/test_entity_types.py::test_resource_definitions` — the `AttributeError` on `client.update` causes `exit_code != 0`.

- [ ] **Step 4: Fix entity_types.update**

Open `cortexapps_cli/commands/entity_types.py`. Replace the entire `update` function (lines 98–111):

```python
@app.command()
def update(
    ctx: typer.Context,
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help=" File containing custom entity definition; can be passed as stdin with -, example: -f-")] = None,
    entity_type: str = typer.Option(..., "--type", "-t", help="The entity type"),
    _print: CommandOptions._print = True,
):
    """
    Update entity type
    """

    client = ctx.obj["client"]
    data = json.loads("".join([line for line in file_input]))

    r = client.put("api/v1/catalog/definitions/" + entity_type, data=data)
    if _print:
        print_output_with_context(ctx, r)
```

- [ ] **Step 5: Run the test to confirm it passes**

```bash
just test tests/test_entity_types.py
```

Expected: `PASSED` for both `test_resource_definitions` and `test_resource_definitions_invalid_icon`.

- [ ] **Step 6: Commit the fix**

```bash
git add cortexapps_cli/commands/entity_types.py tests/test_entity_types.py
git commit -m "$(cat <<'EOF'
fix: entity-types update calls nonexistent client method

CortexClient has no update() method. Replace with put(), add _print
param, and call print_output_with_context so results are displayed.
Harden test to assert exit_code == 0.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: pytest coverage metrics

**Files:**
- Modify: `Justfile` — `test-all` recipe
- Create: `scripts/post_coverage.py`
- Modify: `.github/workflows/test-daily.yml`

**Interfaces:**
- Consumes: `coverage.json` at repo root — written by `--cov-report json:coverage.json`
- `coverage.json` structure used by the script:
  ```json
  {
    "files": {
      "cortexapps_cli/commands/catalog.py": {
        "summary": {
          "covered_lines": 45,
          "num_statements": 60,
          "percent_covered": 75.0,
          "missing_lines": 15
        }
      }
    },
    "totals": {
      "percent_covered": 83.3
    }
  }
  ```
- Produces: two Cortex API calls on the `cli` entity:
  - `cortex custom-metrics add -t cli -k code-coverage-pct -v <float>`
  - `cortex custom-data add -t cli -k pytest-coverage -v '<json-string>'`

- [ ] **Step 1: Add JSON coverage report to Justfile test-all recipe**

Open `Justfile`. In the `test-all` recipe, add `--cov-report json:coverage.json` to the pytest flags. The line currently ends with `--cov-report term-missing tests`. Change it to:

```
# Run all tests
test-all: _setup test-import
   {{pytest}} -n auto -m "not setup and not perf and not functional" --html=report.html --self-contained-html --cov=cortexapps_cli --cov-append --cov-report term-missing --cov-report json:coverage.json tests
```

- [ ] **Step 2: Verify coverage.json is generated locally**

```bash
just test-all
ls -la coverage.json
```

Expected: `coverage.json` exists at repo root, terminal output is unchanged (still shows missing lines table).

- [ ] **Step 3: Create the scripts directory and post_coverage.py**

```bash
mkdir -p scripts
```

Create `scripts/post_coverage.py` with this content:

```python
#!/usr/bin/env python3
"""
Post pytest coverage metrics to Cortex.

Reads coverage.json (generated by pytest-cov --cov-report json:coverage.json)
and posts two things to the 'cli' entity in Cortex:
  1. Total coverage % as a custom metric (code-coverage-pct)
  2. Per-file summary as custom metadata (pytest-coverage)

Requires CORTEX_API_KEY in the environment (or ~/.cortex/config).
"""

import json
import subprocess
import sys
from pathlib import Path


ENTITY_TAG = "cli"
METRIC_KEY = "code-coverage-pct"
CUSTOM_DATA_KEY = "pytest-coverage"
COVERAGE_FILE = Path("coverage.json")


def load_coverage():
    if not COVERAGE_FILE.exists():
        print(f"ERROR: {COVERAGE_FILE} not found. Run tests with --cov-report json:coverage.json first.", file=sys.stderr)
        sys.exit(1)
    with COVERAGE_FILE.open() as f:
        return json.load(f)


def build_simplified_report(coverage):
    files = []
    for filepath, data in coverage["files"].items():
        s = data["summary"]
        files.append({
            "file": filepath,
            "lines_tested": s["covered_lines"],
            "lines_missing": s["missing_lines"],
            "pct": round(s["percent_covered"], 2),
        })
    files.sort(key=lambda x: x["file"])
    return {
        "total_pct": round(coverage["totals"]["percent_covered"], 2),
        "files": files,
    }


def run(cmd):
    print(f"+ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        print(f"ERROR: command failed (exit {result.returncode})", file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)


def post_metric(total_pct):
    run([
        "cortex", "custom-metrics", "add",
        "-t", ENTITY_TAG,
        "-k", METRIC_KEY,
        "-v", str(total_pct),
    ])


def post_custom_data(report):
    import tempfile, os
    payload = {
        "key": CUSTOM_DATA_KEY,
        "description": "pytest coverage report",
        "value": report,
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(payload, f)
        tmp_path = f.name
    try:
        run([
            "cortex", "custom-data", "add",
            "-t", ENTITY_TAG,
            "-f", tmp_path,
        ])
    finally:
        os.unlink(tmp_path)


def main():
    coverage = load_coverage()
    report = build_simplified_report(coverage)

    print(f"Total coverage: {report['total_pct']}%  ({len(report['files'])} files)")

    post_metric(report["total_pct"])
    post_custom_data(report)

    print("Done.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Make the script executable**

```bash
chmod +x scripts/post_coverage.py
```

- [ ] **Step 5: Smoke-test the script locally**

Ensure `CORTEX_API_KEY` is set, then:

```bash
python scripts/post_coverage.py
```

Expected: prints total coverage %, two `cortex` command lines, then "Done." Verify in your Cortex tenant that:
- `code-coverage-pct` metric has a new data point on the `cli` entity
- `pytest-coverage` custom data key on the `cli` entity has the updated per-file JSON

- [ ] **Step 6: Add the post-coverage step to test-daily.yml**

Open `.github/workflows/test-daily.yml`. After the `Test with pytest` step (line 64–66), add:

```yaml
    - name: Post coverage metrics to Cortex
      run: python scripts/post_coverage.py
```

The full jobs.test.steps section should end with:

```yaml
    - name: Test with pytest
      run: |
        just test-all

    - name: Post coverage metrics to Cortex
      run: python scripts/post_coverage.py
```

`CORTEX_API_KEY` is already available as an env var in this workflow — no new secrets needed.

- [ ] **Step 7: Commit the coverage feature**

```bash
git add Justfile scripts/post_coverage.py .github/workflows/test-daily.yml
git commit -m "$(cat <<'EOF'
feat: post pytest coverage metrics to Cortex daily

After the daily test run, post total coverage % as custom metric
code-coverage-pct and per-file summary as custom metadata pytest-coverage
on the cli entity. Uses pytest-cov JSON output (--cov-report json).

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: PR to main

- [ ] **Step 1: Check current version tag**

```bash
git fetch origin --tags
git describe --tags --abbrev=0
```

- [ ] **Step 2: Confirm commits on branch**

```bash
git log $(git describe --tags --abbrev=0)..HEAD --oneline
```

Expected: two commits — one `fix:`, one `feat:`. The `feat:` triggers a **minor** version bump.

- [ ] **Step 3: Run full test suite**

```bash
just test-all
```

Expected: all tests pass.

- [ ] **Step 4: Create PR to main**

```bash
gh pr create --base main --head 227-entity-types-fix-coverage-metrics --title "feat: entity-types update fix + pytest coverage metrics to Cortex" --body "$(cat <<'EOF'
## Summary

- **fix:** `entity-types update` was calling `client.update()` which doesn't exist on `CortexClient` — crashed with `AttributeError` on every invocation. Fixed to use `client.put()`, added `_print` param and output call. Test hardened to assert `exit_code == 0`.
- **feat:** Daily test workflow now posts pytest coverage data to the `cli` entity in Cortex: total % as `code-coverage-pct` custom metric, per-file breakdown as `pytest-coverage` custom metadata.

## Test plan

- [ ] `just test-all` passes locally
- [ ] `cortex entity-types update -t cli-test -f data/run-time/entity-type-update.json` succeeds and prints the updated entity type
- [ ] After merge, trigger `test-daily.yml` manually and verify `code-coverage-pct` metric and `pytest-coverage` custom data appear on the `cli` entity in Cortex

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```
