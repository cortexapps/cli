# Workday Integration Solution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `workday-integration` Cortex CLI solution that bundles a Pied Piper org hierarchy JSON report and a setup script that configures the Cortex Workday integration via API to point at it.

**Architecture:** Static data files (`pied-piper-hierarchy.json`, `configuration.json`) live in the solution bundle and are served publicly via raw.githubusercontent.com. A `setup.py` wizard (extending `SolutionSetup`) checks for an existing Workday config, optionally backs it up, then POSTs the bundled configuration to the Cortex Workday API. No scorecards, no entity types, no external services.

**Tech Stack:** Python 3.11+, `requests`, `SolutionSetup` base class (same pattern as `github-actions-deploy`)

## Global Constraints

- Solution tag: `workday-integration`
- Solution directory: `cortexapps_cli/solutions/workday-integration/`
- Report format: `ONE_EMPLOYEE_ONE_TEAM` hierarchy
- Report URL (baked into configuration.json): `https://raw.githubusercontent.com/cortexapps/cli/main/cortexapps_cli/solutions/workday-integration/data/pied-piper-hierarchy.json`
- Cortex API endpoints (from `cortexapps_cli/commands/integrations_commands/workday.py`):
  - GET existing config: `GET {base_url}/api/v1/workday/default-configuration`
  - Create config: `POST {base_url}/api/v1/workday/configuration`
  - Delete config: `DELETE {base_url}/api/v1/workday/configurations` (note: plural)
- Backup file on replace: `~/.cortex/solutions/workday-integration/backup-config.json`
- `SolutionSetup` must be imported dynamically (same pattern as `github-actions-deploy/setup.py`)
- State file: `~/.cortex/solutions/workday-integration.json` (handled by base class)
- Credentials come from CLI session (`cortex_api_key`, `cortex_base_url` kwargs to `main()`)
- No credential prompts in `collect_prompts()` — only the replace-existing prompt
- `feat:` commit prefix for setup.py (affects CLI deliverable); `chore:` or `docs:` for data/README

---

## File Map

| File | Action |
|------|--------|
| `cortexapps_cli/solutions/workday-integration/data/pied-piper-hierarchy.json` | Create |
| `cortexapps_cli/solutions/workday-integration/data/configuration.json` | Create |
| `cortexapps_cli/solutions/workday-integration/setup.py` | Create |
| `cortexapps_cli/solutions/workday-integration/README.md` | Create |
| `tests/test_workday_setup.py` | Create |

---

## Task 1: Data files

**Files:**
- Create: `cortexapps_cli/solutions/workday-integration/data/pied-piper-hierarchy.json`
- Create: `cortexapps_cli/solutions/workday-integration/data/configuration.json`
- Test: `tests/test_workday_setup.py` (data validation tests only)

**Interfaces:**
- Produces: `DATA_DIR = Path(__file__).parent / "data"` — used by Task 2's `setup.py`
- Produces: `CONFIG_FILE = DATA_DIR / "configuration.json"` — loaded and POSTed in Task 2

- [ ] **Step 1: Create the directory**

```bash
mkdir -p cortexapps_cli/solutions/workday-integration/data
```

- [ ] **Step 2: Write `pied-piper-hierarchy.json`**

Create `cortexapps_cli/solutions/workday-integration/data/pied-piper-hierarchy.json` with this exact content (7 Pied Piper employees, `ONE_EMPLOYEE_ONE_TEAM` format):

```json
{
  "Report_Entry": [
    {
      "email": "erlich.bachman@piedpiper.com",
      "employeeId": "100000",
      "firstName": "Erlich",
      "lastName": "Bachman",
      "managersEmail": "erlich.bachman@piedpiper.com",
      "teamId": "WORKTEAM-1-000",
      "teamName": "PP: Pied Piper",
      "parentTeamId": "NONE"
    },
    {
      "email": "richard.hendricks@piedpiper.com",
      "employeeId": "100001",
      "firstName": "Richard",
      "lastName": "Hendricks",
      "managersEmail": "erlich.bachman@piedpiper.com",
      "teamId": "WORKTEAM-1-001",
      "teamName": "PP: Engineering",
      "parentTeamId": "WORKTEAM-1-000"
    },
    {
      "email": "bertram.gilfoyle@piedpiper.com",
      "employeeId": "100002",
      "firstName": "Bertram",
      "lastName": "Gilfoyle",
      "managersEmail": "richard.hendricks@piedpiper.com",
      "teamId": "WORKTEAM-1-002",
      "teamName": "PP: Platform",
      "parentTeamId": "WORKTEAM-1-001"
    },
    {
      "email": "dinesh.chugtai@piedpiper.com",
      "employeeId": "100003",
      "firstName": "Dinesh",
      "lastName": "Chugtai",
      "managersEmail": "richard.hendricks@piedpiper.com",
      "teamId": "WORKTEAM-1-003",
      "teamName": "PP: Frontend",
      "parentTeamId": "WORKTEAM-1-001"
    },
    {
      "email": "jared.dunn@piedpiper.com",
      "employeeId": "100004",
      "firstName": "Jared",
      "lastName": "Dunn",
      "managersEmail": "erlich.bachman@piedpiper.com",
      "teamId": "WORKTEAM-1-004",
      "teamName": "PP: Operations",
      "parentTeamId": "WORKTEAM-1-000"
    },
    {
      "email": "monica.hall@piedpiper.com",
      "employeeId": "100005",
      "firstName": "Monica",
      "lastName": "Hall",
      "managersEmail": "jared.dunn@piedpiper.com",
      "teamId": "WORKTEAM-1-005",
      "teamName": "PP: People Ops",
      "parentTeamId": "WORKTEAM-1-004"
    },
    {
      "email": "nelson.bighetti@piedpiper.com",
      "employeeId": "100006",
      "firstName": "Nelson",
      "lastName": "Bighetti",
      "managersEmail": "bertram.gilfoyle@piedpiper.com",
      "teamId": "WORKTEAM-1-006",
      "teamName": "PP: Infrastructure",
      "parentTeamId": "WORKTEAM-1-002"
    }
  ]
}
```

- [ ] **Step 3: Write `configuration.json`**

Create `cortexapps_cli/solutions/workday-integration/data/configuration.json` with this exact content:

```json
{
  "username": "ISU_Cortex",
  "ownershipReportUrl": "https://raw.githubusercontent.com/cortexapps/cli/main/cortexapps_cli/solutions/workday-integration/data/pied-piper-hierarchy.json",
  "reportMappingV2": {
    "email": { "columnName": "email" },
    "employeeId": { "columnName": "employeeId" },
    "firstName": { "columnName": "firstName" },
    "lastName": { "columnName": "lastName" },
    "managerEmail": { "columnName": "managersEmail" },
    "employeeRole": null,
    "rootTeams": [],
    "teamListFields": null,
    "fallbackFields": {
      "teamId": { "columnName": "teamId" },
      "teamName": { "columnName": "teamName" },
      "fieldOnParentNode": { "columnName": "teamId" },
      "fieldOnChildNode": { "columnName": "parentTeamId" }
    },
    "type": "ONE_EMPLOYEE_ONE_TEAM"
  },
  "password": "asdf"
}
```

- [ ] **Step 4: Write failing data validation tests**

Create `tests/test_workday_setup.py` with these data-validation tests only (setup.py tests come in Task 2):

```python
import json
from pathlib import Path

DATA_DIR = Path("cortexapps_cli/solutions/workday-integration/data")
REPORT_URL = (
    "https://raw.githubusercontent.com/cortexapps/cli/main"
    "/cortexapps_cli/solutions/workday-integration/data/pied-piper-hierarchy.json"
)


def test_hierarchy_json_is_valid():
    data = json.loads((DATA_DIR / "pied-piper-hierarchy.json").read_text())
    assert "Report_Entry" in data
    assert len(data["Report_Entry"]) == 7


def test_hierarchy_has_root_employee():
    data = json.loads((DATA_DIR / "pied-piper-hierarchy.json").read_text())
    roots = [e for e in data["Report_Entry"] if e["managersEmail"] == e["email"]]
    assert len(roots) == 1
    assert roots[0]["email"] == "erlich.bachman@piedpiper.com"


def test_hierarchy_has_root_team():
    data = json.loads((DATA_DIR / "pied-piper-hierarchy.json").read_text())
    roots = [e for e in data["Report_Entry"] if e["parentTeamId"] == "NONE"]
    assert len(roots) == 1
    assert roots[0]["teamId"] == "WORKTEAM-1-000"


def test_hierarchy_required_fields():
    data = json.loads((DATA_DIR / "pied-piper-hierarchy.json").read_text())
    required = {"email", "employeeId", "firstName", "lastName", "managersEmail",
                "teamId", "teamName", "parentTeamId"}
    for entry in data["Report_Entry"]:
        assert required <= entry.keys(), f"Missing fields in entry: {entry}"


def test_configuration_json_is_valid():
    config = json.loads((DATA_DIR / "configuration.json").read_text())
    assert config["ownershipReportUrl"] == REPORT_URL
    assert config["reportMappingV2"]["type"] == "ONE_EMPLOYEE_ONE_TEAM"
    assert "password" in config
    assert "username" in config


def test_configuration_mapping_fields():
    config = json.loads((DATA_DIR / "configuration.json").read_text())
    mapping = config["reportMappingV2"]
    assert mapping["email"]["columnName"] == "email"
    assert mapping["managerEmail"]["columnName"] == "managersEmail"
    ff = mapping["fallbackFields"]
    assert ff["fieldOnParentNode"]["columnName"] == "teamId"
    assert ff["fieldOnChildNode"]["columnName"] == "parentTeamId"
```

- [ ] **Step 5: Run tests to verify they fail (data files don't exist yet)**

```bash
poetry run pytest tests/test_workday_setup.py -v
```

Expected: FAIL (FileNotFoundError or similar — data files not created yet).

If files are already created from Steps 2–3, the tests should PASS. That is also fine — proceed.

- [ ] **Step 6: Run tests to verify they pass**

```bash
poetry run pytest tests/test_workday_setup.py::test_hierarchy_json_is_valid \
  tests/test_workday_setup.py::test_configuration_json_is_valid -v
```

Expected: all 6 data tests PASS.

- [ ] **Step 7: Commit**

```bash
git add cortexapps_cli/solutions/workday-integration/data/ tests/test_workday_setup.py
git commit -m "chore: add Pied Piper hierarchy data and configuration for workday-integration solution"
```

---

## Task 2: setup.py

**Files:**
- Create: `cortexapps_cli/solutions/workday-integration/setup.py`
- Modify: `tests/test_workday_setup.py` (add setup script tests)

**Interfaces:**
- Consumes: `cortexapps_cli/solutions/workday-integration/data/configuration.json` (Task 1)
- Consumes: `SolutionSetup` base class from `cortexapps_cli/solutions/_lib/setup_base.py`
- Produces: `main(cortex_api_key=None, cortex_base_url=None, no_prompt=False, **kwargs)` — called by `_run_post_install_script` in `cortexapps_cli/commands/solutions.py`
- Produces: `SETUP_DESCRIPTION` module-level string — displayed by `cortex solutions install`

**Key facts about the `_run_post_install_script` caller (do not modify this file):**
```python
# From cortexapps_cli/commands/solutions.py:
kwargs["cortex_api_key"] = client.api_key
kwargs["cortex_base_url"] = client.base_url
kwargs["no_prompt"] = no_prompt
module.main(**kwargs)
```
So `main()` receives `cortex_api_key`, `cortex_base_url`, and `no_prompt` as keyword args.

**Cortex API endpoints to call:**
- Check existing: `GET {base_url}/api/v1/workday/default-configuration`
- Delete existing: `DELETE {base_url}/api/v1/workday/configurations` (plural `configurations`)
- Create new: `POST {base_url}/api/v1/workday/configuration` (singular `configuration`)

- [ ] **Step 1: Write failing tests for the setup script**

Append to `tests/test_workday_setup.py`:

```python
import importlib.util
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


def load_setup_module():
    spec = importlib.util.spec_from_file_location(
        "workday_setup",
        "cortexapps_cli/solutions/workday-integration/setup.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mod():
    return load_setup_module()


@pytest.fixture
def setup(mod, tmp_path):
    return mod.WorkdayIntegrationSetup(
        cortex_api_key="crt_test",
        cortex_base_url="https://api.getcortexapp.com",
        state_dir=tmp_path,
    )


def test_solution_tag(mod):
    assert mod.WorkdayIntegrationSetup.solution_tag == "workday-integration"


def test_setup_description(mod):
    assert "Workday" in mod.SETUP_DESCRIPTION


def test_collect_prompts_is_noop(setup):
    # collect_prompts() must not raise and must not call input()
    with patch("builtins.input", side_effect=AssertionError("should not prompt")):
        setup.collect_prompts()  # no exception = pass


def test_check_existing_no_config_proceeds(setup):
    resp_404 = MagicMock(status_code=404)
    resp_404.raise_for_status = MagicMock()
    with patch("requests.get", return_value=resp_404):
        # Should return without prompting or raising
        setup._check_and_replace_existing()


def test_check_existing_user_declines_exits(setup):
    resp_200 = MagicMock(status_code=200)
    resp_200.raise_for_status = MagicMock()
    resp_200.json.return_value = {"username": "ISU_Cortex"}
    with patch("requests.get", return_value=resp_200), \
         patch("builtins.input", return_value="n"):
        with pytest.raises(SystemExit) as exc_info:
            setup._check_and_replace_existing()
        assert exc_info.value.code == 0


def test_check_existing_user_accepts_backs_up_and_deletes(setup, tmp_path):
    existing = {"username": "ISU_Cortex", "ownershipReportUrl": "https://old.example.com"}
    resp_200 = MagicMock(status_code=200)
    resp_200.raise_for_status = MagicMock()
    resp_200.json.return_value = existing
    resp_del = MagicMock(status_code=204)
    resp_del.raise_for_status = MagicMock()

    backup_dir = tmp_path / "workday-integration"

    with patch("requests.get", return_value=resp_200), \
         patch("requests.delete", return_value=resp_del) as mock_delete, \
         patch("builtins.input", return_value="y"), \
         patch("pathlib.Path.home", return_value=tmp_path):
        setup._check_and_replace_existing()

    mock_delete.assert_called_once()
    delete_url = mock_delete.call_args.args[0]
    assert "configurations" in delete_url   # plural endpoint

    backup_file = tmp_path / ".cortex" / "solutions" / "workday-integration" / "backup-config.json"
    assert backup_file.exists()
    assert json.loads(backup_file.read_text()) == existing


def test_configure_integration_posts_correct_payload(setup):
    resp = MagicMock(ok=True, status_code=200)
    with patch("requests.post", return_value=resp) as mock_post:
        setup._configure_integration()

    mock_post.assert_called_once()
    url = mock_post.call_args.args[0]
    assert url.endswith("/api/v1/workday/configuration")

    payload = mock_post.call_args.kwargs["json"]
    assert payload["reportMappingV2"]["type"] == "ONE_EMPLOYEE_ONE_TEAM"
    assert "pied-piper-hierarchy.json" in payload["ownershipReportUrl"]


def test_configure_integration_raises_on_failure(setup):
    resp = MagicMock(ok=False, status_code=400, text="Bad Request")
    with patch("requests.post", return_value=resp):
        with pytest.raises(RuntimeError, match="Failed to configure"):
            setup._configure_integration()


def test_configure_integration_idempotent(setup, tmp_path):
    setup.mark_done("configure")
    with patch("requests.post") as mock_post:
        setup._configure_integration()
    mock_post.assert_not_called()


def test_main_callable(mod):
    assert callable(mod.main)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
poetry run pytest tests/test_workday_setup.py -k "not test_hierarchy and not test_configuration" -v
```

Expected: FAIL with `ModuleNotFoundError` or `FileNotFoundError` (setup.py doesn't exist yet).

- [ ] **Step 3: Create `setup.py`**

Create `cortexapps_cli/solutions/workday-integration/setup.py` with this exact content:

```python
"""
Post-install setup script for the workday-integration solution.
Configures the Cortex Workday integration to sync the Pied Piper org hierarchy.
Run via: cortex solutions post-install -s workday-integration
"""

SETUP_DESCRIPTION = (
    "This solution includes a post-install setup script that will configure "
    "the Cortex Workday integration to sync the Pied Piper org hierarchy."
)

import json
import sys
from pathlib import Path
import requests

try:
    from cortexapps_cli.solutions._lib.setup_base import SolutionSetup
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from _lib.setup_base import SolutionSetup

DATA_DIR = Path(__file__).parent / "data"
CONFIG_FILE = DATA_DIR / "configuration.json"


class WorkdayIntegrationSetup(SolutionSetup):
    solution_tag = "workday-integration"

    def __init__(
        self,
        cortex_api_key: str = None,
        cortex_base_url: str = None,
        no_prompt: bool = False,
        **kwargs,
    ):
        super().__init__(no_prompt=no_prompt, **kwargs)
        self._api_key = cortex_api_key or ""
        self._base_url = (cortex_base_url or "https://api.getcortexapp.com").rstrip("/")

    def _cortex_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def collect_prompts(self) -> None:
        pass  # credentials come from CLI session

    def _check_and_replace_existing(self) -> None:
        """Check for an existing Workday config; backup and delete it if user confirms."""
        r = requests.get(
            f"{self._base_url}/api/v1/workday/default-configuration",
            headers=self._cortex_headers(),
        )
        if r.status_code == 404:
            return  # no existing config — proceed
        r.raise_for_status()

        if not self.confirm("Existing Workday integration found. Replace it?", default=False):
            print("Keeping existing Workday integration. Exiting.")
            raise SystemExit(0)

        # Back up the existing config
        backup_dir = Path.home() / ".cortex" / "solutions" / "workday-integration"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_file = backup_dir / "backup-config.json"
        backup_file.write_text(json.dumps(r.json(), indent=2))
        print(f"  Backed up existing config to {backup_file}")

        # Delete the existing config
        del_r = requests.delete(
            f"{self._base_url}/api/v1/workday/configurations",
            headers=self._cortex_headers(),
        )
        del_r.raise_for_status()

    def _configure_integration(self) -> None:
        """POST the bundled Workday integration configuration."""
        if self.already_done("configure"):
            return "Already configured (skipped)"
        config = json.loads(CONFIG_FILE.read_text())
        r = requests.post(
            f"{self._base_url}/api/v1/workday/configuration",
            headers=self._cortex_headers(),
            json=config,
        )
        if not r.ok:
            raise RuntimeError(
                f"Failed to configure Workday integration: {r.status_code} {r.text}"
            )
        self.mark_done("configure")

    def steps(self) -> list:
        return [
            ("Check for existing Workday integration", self._check_and_replace_existing),
            ("Configure Workday integration", self._configure_integration),
        ]

    def post_steps(self) -> None:
        print("\n✓ Workday integration configured with the Pied Piper org hierarchy.\n")
        print("Next: trigger the import in Cortex:")
        print("  Catalog → All Entities → Import Entities\n")
        print("Then check your team hierarchy to see the Pied Piper org chart.")


def main(cortex_api_key=None, cortex_base_url=None, no_prompt=False, **kwargs):
    WorkdayIntegrationSetup(
        cortex_api_key=cortex_api_key,
        cortex_base_url=cortex_base_url,
        no_prompt=no_prompt,
    ).run()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run all setup script tests**

```bash
poetry run pytest tests/test_workday_setup.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add cortexapps_cli/solutions/workday-integration/setup.py tests/test_workday_setup.py
git commit -m "feat: add workday-integration solution setup script"
```

---

## Task 3: README

**Files:**
- Create: `cortexapps_cli/solutions/workday-integration/README.md`

**Interfaces:**
- Consumes: nothing from prior tasks (pure documentation)

- [ ] **Step 1: Create `README.md`**

Create `cortexapps_cli/solutions/workday-integration/README.md` with this content:

```markdown
---
name: Workday Integration
description: Configure the Cortex Workday integration with a sample Pied Piper org hierarchy to sync employees and teams into your service catalog.
---

# Workday Integration

Get the Cortex Workday integration running in minutes using a pre-built Pied Piper org hierarchy. After install, trigger a sync to see employees and teams appear in your catalog — including the full team hierarchy.

## What's Included

- **Pied Piper org data:** 7 employees across 4 levels of hierarchy (Erlich → Richard → Gilfoyle/Dinesh, Jared → Monica, Bachman → Big Head)
- **Integration config:** field mapping and report URL pre-configured, pointing at the hosted data
- **Setup script:** one-command configuration of the Cortex Workday integration via API

## Quick Start

1. Install the solution:

   ```
   cortex solutions install -s workday-integration
   ```

2. Follow the post-install setup prompts, or run later:

   ```
   cortex solutions post-install -s workday-integration
   ```

3. Trigger the import in Cortex:

   **Catalog → All Entities → Import Entities**

4. Check your team hierarchy to see the Pied Piper org chart.

## Org Hierarchy

```
PP: Pied Piper (Erlich Bachman)
├── PP: Engineering (Richard Hendricks)
│   ├── PP: Platform (Bertram Gilfoyle)
│   │   └── PP: Infrastructure (Nelson Bighetti)
│   └── PP: Frontend (Dinesh Chugtai)
└── PP: Operations (Jared Dunn)
    └── PP: People Ops (Monica Hall)
```

## How It Works

The setup script calls the Cortex Workday integration API to configure a report URL pointing at `pied-piper-hierarchy.json` hosted in this repository. Cortex fetches the report and syncs employees and teams into your catalog on the next import run.

## Adapting to Real Workday Data

To point the integration at a real Workday RaaS report:

1. Go to **Settings → Integrations → Workday** in the Cortex UI
2. Update the **Report URL** to your Workday RaaS endpoint
3. Set your real **username** and **password**
4. Trigger a new import

The field mapping (`reportMappingV2`) in `data/configuration.json` matches the standard Cortex Workday report format and works unchanged for real Workday data that uses the same column names.
```

- [ ] **Step 2: Run the full test suite to confirm nothing is broken**

```bash
poetry run pytest tests/test_workday_setup.py tests/test_solutions_postinstall.py tests/test_setup_base.py -v
```

Expected: all tests PASS.

- [ ] **Step 3: Commit**

```bash
git add cortexapps_cli/solutions/workday-integration/README.md
git commit -m "docs: add README for workday-integration solution"
```
