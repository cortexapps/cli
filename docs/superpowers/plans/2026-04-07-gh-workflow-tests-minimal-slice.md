# GitHub Workflow Action Block Tests — Minimal Vertical Slice

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and locally run one end-to-end functional test (List branches) that exercises a Cortex GitHub workflow action block.

**Architecture:** Add `cortex workflows run` and `get-run` CLI commands hitting the public Workflows Run API. Create one workflow YAML for `github.listBranches`. Build test infrastructure (conftest.py, gh_helpers.py) with safeguards. Wire it together in a single pytest test.

**Tech Stack:** Python 3.11+, Typer, pytest, `gh` CLI, Cortex Workflows Run API

---

## File Structure

| File | Responsibility |
|------|---------------|
| `cortexapps_cli/commands/workflows.py` | Modify: add `run` and `get-run` commands |
| `data/functional/workflows/gh-list-branches.yaml` | Create: workflow YAML for list-branches action |
| `tests/functional/conftest.py` | Create: session fixtures (org validation, repo, import) |
| `tests/functional/gh_helpers.py` | Create: GitHub helper functions and workflow runner |
| `tests/functional/test_functional_import.py` | Create: import functional test data |
| `tests/functional/test_gh_branches.py` | Create: list-branches test |
| `tests/functional/test_sample.py` | Delete: replaced by real tests |
| `Justfile` | Modify: add `_check-functional-env` recipe |

---

### Task 1: Add `cortex workflows run` command

**Files:**
- Modify: `cortexapps_cli/commands/workflows.py`

- [ ] **Step 1: Add the `run` command to workflows.py**

Add this after the existing `create` command at the end of the file:

```python
@app.command()
def run(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag or unique identifier for the workflow"),
    scope: str = typer.Option("GLOBAL", "--scope", "-s", help="Scope type: GLOBAL or ENTITY"),
    entity: str = typer.Option(None, "--entity", "-e", help="Entity tag (required when scope is ENTITY)"),
    run_as: str = typer.Option(None, "--run-as", help="Email of user to run the workflow as"),
    context: str = typer.Option(None, "--context", "-x", help="JSON string for initialContext"),
    context_file: Annotated[typer.FileText, typer.Option("--context-file", help="JSON file for initialContext")] = None,
    wait: bool = typer.Option(False, "--wait", "-w", help="Poll until the run completes"),
    timeout: int = typer.Option(300, "--timeout", help="Max seconds to wait when --wait is used"),
):
    """
    Run a workflow.  API key must have the Run workflows permission.
    The workflow must have isRunnableViaApi set to true.
    """
    import time as time_module

    client = ctx.obj["client"]

    # Build scope payload
    if scope.upper() == "ENTITY":
        if not entity:
            raise typer.BadParameter("--entity is required when --scope is ENTITY")
        scope_payload = {"type": "ENTITY", "entityId": entity}
    else:
        scope_payload = {"type": "GLOBAL"}

    # Build request body
    body = {"scope": scope_payload}

    if run_as:
        body["runAs"] = run_as

    # Handle initialContext from --context or --context-file
    if context and context_file:
        raise typer.BadParameter("Cannot specify both --context and --context-file")
    if context:
        body["initialContext"] = json.loads(context)
    elif context_file:
        body["initialContext"] = json.load(context_file)

    r = client.post(f"api/v1/workflows/{tag}/runs", data=body)

    if not wait:
        print_output(r)
        return

    # Poll until completed or timeout
    run_id = r.get("id")
    if not run_id:
        print_output(r)
        return

    start = time_module.time()
    while time_module.time() - start < timeout:
        time_module.sleep(2)
        r = client.get(f"api/v1/workflows/{tag}/runs/{run_id}")
        status = r.get("status", "").upper()
        if status in ("COMPLETED", "FAILED", "CANCELLED"):
            break

    print_output(r)
```

- [ ] **Step 2: Verify the command registers**

Run:
```bash
poetry run cortex workflows run --help
```

Expected: Help output showing `--tag`, `--scope`, `--context`, `--wait`, `--timeout` options.

- [ ] **Step 3: Commit**

```bash
git add cortexapps_cli/commands/workflows.py
git commit -m "feat: add 'cortex workflows run' command for triggering workflow runs"
```

---

### Task 2: Add `cortex workflows get-run` command

**Files:**
- Modify: `cortexapps_cli/commands/workflows.py`

- [ ] **Step 1: Add the `get-run` command to workflows.py**

Add this after the `run` command:

```python
@app.command("get-run")
def get_run(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag or unique identifier for the workflow"),
    run_id: str = typer.Option(..., "--run-id", "-r", help="The run ID"),
):
    """
    Get details of a workflow run.  API key must have the View workflow runs permission.
    """
    client = ctx.obj["client"]
    r = client.get(f"api/v1/workflows/{tag}/runs/{run_id}")
    print_output(r)
```

- [ ] **Step 2: Verify the command registers**

Run:
```bash
poetry run cortex workflows get-run --help
```

Expected: Help output showing `--tag` and `--run-id` options.

- [ ] **Step 3: Commit**

```bash
git add cortexapps_cli/commands/workflows.py
git commit -m "feat: add 'cortex workflows get-run' command"
```

---

### Task 3: Create the list-branches workflow YAML

**Files:**
- Create: `data/functional/workflows/gh-list-branches.yaml`

- [ ] **Step 1: Create the data directory and workflow YAML**

```bash
mkdir -p data/functional/workflows
```

Write `data/functional/workflows/gh-list-branches.yaml`:

```yaml
name: "Functional Test: List branches"
tag: func-test-gh-list-branches
description: Functional test for the github.listBranches action block
isDraft: false
isRunnableViaApi: true
filter:
  type: GLOBAL
actions:
- name: List branches
  slug: list-branches
  schema:
    type: ADVANCED_HTTP_REQUEST
    actionIdentifier: github.listBranches
    integrationAlias: null
    inputs:
      repo: "{{context.initialContext.repo}}"
  outgoingActions: []
  isRootAction: true
```

- [ ] **Step 2: Commit**

```bash
git add data/functional/workflows/gh-list-branches.yaml
git commit -m "feat: add list-branches workflow YAML for functional tests"
```

---

### Task 4: Create `tests/functional/gh_helpers.py`

**Files:**
- Create: `tests/functional/gh_helpers.py`

- [ ] **Step 1: Write gh_helpers.py**

```python
import json
import os
import subprocess
import time

from tests.helpers.utils import cli, ReturnType

RESOURCE_PREFIX = "cli-functional-test-"


def get_env(name):
    """Get a required environment variable or raise."""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Required environment variable {name} is not set")
    return value


def gh_api(method, path, input_data=None):
    """Call the GitHub API via the gh CLI.

    Returns parsed JSON response. Raises on non-zero exit code.
    """
    pat = get_env("GITHUB_TEST_PAT")
    cmd = ["gh", "api", "-X", method, path, "-H", "Accept: application/vnd.github+json"]

    env = {**os.environ, "GH_TOKEN": pat}

    if input_data is not None:
        cmd.extend(["--input", "-"])
        result = subprocess.run(
            cmd,
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            env=env,
        )
    else:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)

    if result.returncode != 0:
        raise RuntimeError(f"gh api {method} {path} failed: {result.stderr}")

    if not result.stdout.strip():
        return None

    return json.loads(result.stdout)


def safe_delete_repo(repo_full_name):
    """Delete a GitHub repo, but only if the name matches the safety prefix."""
    # repo_full_name is "org/repo-name"
    repo_name = repo_full_name.split("/")[-1]
    if not repo_name.startswith(RESOURCE_PREFIX):
        raise RuntimeError(
            f"Refusing to delete repo '{repo_full_name}' — "
            f"name does not start with '{RESOURCE_PREFIX}'"
        )
    pat = get_env("GITHUB_TEST_PAT")
    env = {**os.environ, "GH_TOKEN": pat}
    subprocess.run(
        ["gh", "repo", "delete", repo_full_name, "--yes"],
        capture_output=True,
        text=True,
        env=env,
    )


def safe_delete_team(org, team_slug):
    """Delete a GitHub team, but only if the slug matches the safety prefix."""
    if not team_slug.startswith(RESOURCE_PREFIX):
        raise RuntimeError(
            f"Refusing to delete team '{team_slug}' — "
            f"name does not start with '{RESOURCE_PREFIX}'"
        )
    gh_api("DELETE", f"/orgs/{org}/teams/{team_slug}")


def validate_test_org(org):
    """Verify the org has the cortex-cli-functional-test safety marker.

    Checks for a custom property 'cortex-cli-functional-test' set to 'true'.
    Raises RuntimeError if not found.
    """
    # List custom properties for the org
    try:
        props = gh_api("GET", f"/orgs/{org}/properties/values")
    except RuntimeError:
        raise RuntimeError(
            f"Cannot read custom properties for org '{org}'. "
            f"Ensure GITHUB_TEST_PAT has admin:org scope."
        )

    # props is a list of repo property objects; we need org-level properties
    # Try the org custom properties endpoint
    try:
        org_props = gh_api("GET", f"/orgs/{org}/custom-properties")
    except RuntimeError:
        org_props = []

    # Check for the safety marker in org custom properties
    found = False
    if isinstance(org_props, list):
        for prop in org_props:
            if prop.get("property_name") == "cortex-cli-functional-test":
                found = True
                break

    if not found:
        raise RuntimeError(
            f"Org '{org}' does not have custom property 'cortex-cli-functional-test'. "
            f"This safety check prevents accidental use of production orgs. "
            f"Create this custom property in your test org's settings."
        )


def create_test_repo(org, repo_name):
    """Create a test repo with README and safety custom property."""
    full_name = f"{org}/{repo_name}"
    gh_api("POST", f"/orgs/{org}/repos", input_data={
        "name": repo_name,
        "auto_init": True,
        "private": True,
        "description": "Ephemeral repo for Cortex CLI functional tests",
    })

    # Set the cli-functional-test-deletable custom property
    try:
        gh_api("PATCH", f"/orgs/{org}/properties/values", input_data={
            "repository_names": [repo_name],
            "properties": [
                {"property_name": "cli-functional-test-deletable", "value": "true"}
            ],
        })
    except RuntimeError:
        # Custom property may not exist yet; non-fatal for MVP
        pass

    return full_name


def get_default_branch_sha(repo_full_name):
    """Get the SHA of the HEAD commit on the default branch."""
    result = gh_api("GET", f"/repos/{repo_full_name}/commits/main")
    return result["sha"]


def run_workflow(tag, initial_context, wait=True, timeout=120):
    """Trigger a Cortex workflow via the CLI and return the result.

    Args:
        tag: Workflow tag
        initial_context: Dict of values to pass as initialContext
        wait: If True, poll until run completes
        timeout: Max seconds to wait

    Returns:
        Parsed JSON response from the workflow run
    """
    params = [
        "workflows", "run",
        "-t", tag,
        "--context", json.dumps(initial_context),
    ]
    if wait:
        params.extend(["--wait", "--timeout", str(timeout)])

    return cli(params)


def wait_for_workflow_run(tag, run_id, timeout=120):
    """Poll a workflow run until it completes or times out.

    Returns the final run response dict.
    """
    start = time.time()
    while time.time() - start < timeout:
        result = cli(["workflows", "get-run", "-t", tag, "-r", run_id])
        status = result.get("status", "").upper()
        if status in ("COMPLETED", "FAILED", "CANCELLED"):
            return result
        time.sleep(2)

    raise TimeoutError(f"Workflow run {run_id} did not complete within {timeout}s")
```

- [ ] **Step 2: Commit**

```bash
git add tests/functional/gh_helpers.py
git commit -m "feat: add GitHub helper functions for functional tests"
```

---

### Task 5: Create `tests/functional/conftest.py`

**Files:**
- Create: `tests/functional/conftest.py`
- Delete: `tests/functional/test_sample.py`

- [ ] **Step 1: Write conftest.py**

```python
import os
import uuid

import pytest

from tests.functional.gh_helpers import (
    RESOURCE_PREFIX,
    create_test_repo,
    get_default_branch_sha,
    get_env,
    safe_delete_repo,
    validate_test_org,
)
from tests.helpers.utils import cli, ReturnType


@pytest.fixture(scope="session")
def gh_test_org():
    """Validate the test org exists and has the safety marker."""
    org = get_env("GITHUB_TEST_ORG")
    validate_test_org(org)
    return org


@pytest.fixture(scope="session")
def gh_test_repo(gh_test_org):
    """Create an ephemeral test repo, yield its full name, then delete it."""
    short_id = uuid.uuid4().hex[:8]
    repo_name = f"{RESOURCE_PREFIX}{short_id}"
    full_name = create_test_repo(gh_test_org, repo_name)
    yield full_name
    safe_delete_repo(full_name)


@pytest.fixture(scope="session")
def gh_default_sha(gh_test_repo):
    """Get the SHA of the default branch HEAD commit in the test repo."""
    return get_default_branch_sha(gh_test_repo)


@pytest.fixture(scope="session")
def import_functional_workflows():
    """Import all functional test workflow YAMLs into Cortex."""
    result = cli(
        ["backup", "import", "-d", "data/functional"],
        return_type=ReturnType.STDOUT,
    )
    # backup import prints results to stdout; we just need it to not crash
    return result
```

- [ ] **Step 2: Delete the sample test**

```bash
rm tests/functional/test_sample.py
```

- [ ] **Step 3: Commit**

```bash
git add tests/functional/conftest.py
git rm tests/functional/test_sample.py
git commit -m "feat: add session fixtures for functional tests"
```

---

### Task 6: Create `tests/functional/test_functional_import.py`

**Files:**
- Create: `tests/functional/test_functional_import.py`

- [ ] **Step 1: Write the import test**

```python
import pytest
from tests.helpers.utils import cli, ReturnType


@pytest.mark.setup
def test():
    """Import functional test data (workflow YAMLs) into Cortex."""
    response = cli(
        ["backup", "import", "-d", "data/functional"],
        return_type=ReturnType.STDOUT,
    )
    print(response)
```

- [ ] **Step 2: Commit**

```bash
git add tests/functional/test_functional_import.py
git commit -m "feat: add functional test data import test"
```

---

### Task 7: Create the list-branches functional test

**Files:**
- Create: `tests/functional/test_gh_branches.py`

- [ ] **Step 1: Write the test**

```python
import pytest
from tests.functional.gh_helpers import gh_api, run_workflow


@pytest.mark.functional
def test_gh_list_branches(gh_test_repo, gh_default_sha, import_functional_workflows):
    """Test the github.listBranches workflow action block.

    Triggers a Cortex workflow that calls GitHub's list-branches API,
    then verifies the response via the gh CLI.
    """
    # 1. Trigger the workflow
    result = run_workflow(
        tag="func-test-gh-list-branches",
        initial_context={"repo": gh_test_repo},
    )

    # 2. Verify the Cortex workflow run completed successfully
    status = result.get("status", "").upper()
    assert status == "COMPLETED", (
        f"Workflow run status was '{status}', expected 'COMPLETED'. "
        f"Full response: {result}"
    )

    # 3. Verify GitHub side-effect: branches exist on the repo
    branches = gh_api("GET", f"/repos/{gh_test_repo}/branches")
    branch_names = [b["name"] for b in branches]
    assert "main" in branch_names, (
        f"Expected 'main' branch in repo {gh_test_repo}, got: {branch_names}"
    )
```

- [ ] **Step 2: Commit**

```bash
git add tests/functional/test_gh_branches.py
git commit -m "feat: add list-branches functional test"
```

---

### Task 8: Add Justfile env var checks

**Files:**
- Modify: `Justfile`

- [ ] **Step 1: Add the env var check recipe and update test-functional**

Add env var exports and the `_check-functional-env` recipe. Update `test-functional` to depend on it.

The new Justfile should have these env var exports added after the existing ones:

```
export GITHUB_TEST_ORG := env('GITHUB_TEST_ORG', "")
export GITHUB_TEST_PAT := env('GITHUB_TEST_PAT', "")
export GITHUB_TEST_USERNAME := env('GITHUB_TEST_USERNAME', "")
```

Add the check recipe before `test-functional`:

```just
_check-functional-env:
   @test -n "$GITHUB_TEST_ORG" || (echo "ERROR: GITHUB_TEST_ORG is not set" && exit 1)
   @test -n "$GITHUB_TEST_PAT" || (echo "ERROR: GITHUB_TEST_PAT is not set" && exit 1)
   @test -n "$GITHUB_TEST_USERNAME" || (echo "ERROR: GITHUB_TEST_USERNAME is not set" && exit 1)
   @which gh > /dev/null 2>&1 || (echo "ERROR: gh CLI is not installed" && exit 1)
```

Update `test-functional` dependency chain:

```just
test-functional: _check-functional-env test-functional-import
```

- [ ] **Step 2: Verify env var check works**

Run without env vars set:
```bash
just test-functional
```

Expected: `ERROR: GITHUB_TEST_ORG is not set` and exit code 1.

- [ ] **Step 3: Commit**

```bash
git add Justfile
git commit -m "feat: add env var checks for functional tests in Justfile"
```

---

### Task 9: Local end-to-end test run

This is not a code task — it's the manual local verification.

- [ ] **Step 1: Set environment variables**

```bash
export GITHUB_TEST_ORG=<your-test-org>
export GITHUB_TEST_PAT=<your-github-pat>
export GITHUB_TEST_USERNAME=<a-github-username>
```

- [ ] **Step 2: Verify the test org has the safety marker**

```bash
gh api /orgs/$GITHUB_TEST_ORG/custom-properties -H "Authorization: token $GITHUB_TEST_PAT"
```

If `cortex-cli-functional-test` property doesn't exist, create it in the org's Settings > Custom Properties.

- [ ] **Step 3: Verify the workflow run API feature flag is enabled**

```bash
poetry run cortex workflows run -t func-test-gh-list-branches --context '{"repo": "test"}' 2>&1
```

If you see `HTTP Error 403: Running a workflow is not enabled`, the LaunchDarkly flag needs to be enabled for your tenant.

- [ ] **Step 4: Import functional test data**

```bash
just test-functional-import
```

Expected: Workflow `func-test-gh-list-branches` imported successfully.

- [ ] **Step 5: Run the test**

```bash
PYTHONPATH=. poetry run pytest -rA -v -s -m functional tests/functional/test_gh_branches.py
```

Expected: 1 test passes. Output shows workflow triggered, status COMPLETED, main branch verified.

- [ ] **Step 6: Verify cleanup**

After the test completes, the ephemeral repo should be deleted. Check:

```bash
gh api /orgs/$GITHUB_TEST_ORG/repos --jq '.[].name' -H "Authorization: token $GITHUB_TEST_PAT" | grep cli-functional-test
```

Expected: No repos with the `cli-functional-test-` prefix remain.
