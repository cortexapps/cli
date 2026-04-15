# User-Agent Header Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `User-Agent: cortexapps-cli/<version>` header to all CLI API requests so usage can be tracked in DataDog.

**Architecture:** Resolve the package version in `CortexClient.__init__()` using `importlib.metadata`, then inject the `User-Agent` header in the `request()` method. One unit test using the `responses` mock library to verify the header is sent.

**Tech Stack:** Python, requests, importlib.metadata, responses (test mock)

---

### Task 1: Create GitHub Issue

- [ ] **Step 1: Create the issue**

```bash
gh issue create --title "feat: Add User-Agent header to CLI API requests for usage tracking" --body "Add a User-Agent header (cortexapps-cli/<version>) to all HTTP requests made by CortexClient so CLI usage can be identified and tracked in DataDog.

## Motivation
There is currently no way to distinguish CLI-originated API traffic from other sources in DataDog logs.

## Approach
- Set User-Agent header on all requests in CortexClient.request()
- Version resolved via importlib.metadata.version()
- Format: cortexapps-cli/<version> (e.g. cortexapps-cli/1.9.1)
- No server-side changes required — User-Agent is already logged and indexed in DataDog"
```

- [ ] **Step 2: Note the issue number for the branch name**

---

### Task 2: Create Feature Branch

- [ ] **Step 1: Create and switch to feature branch**

```bash
git checkout -b <issue-number>-user-agent-header
```

---

### Task 3: Write Failing Test

**Files:**
- Create: `tests/test_user_agent.py`

- [ ] **Step 1: Write the test**

```python
from tests.helpers.utils import *

@responses.activate
def test_user_agent_header_is_set():
    """Verify that all API requests include a User-Agent header identifying the CLI."""
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/catalog", json={"entities": [], "total": 0, "page": 0, "totalPages": 0}, status=200)
    cli(["catalog", "list", "-p", "0"])
    assert len(responses.calls) == 1
    user_agent = responses.calls[0].request.headers.get("User-Agent", "")
    assert user_agent.startswith("cortexapps-cli/")

@responses.activate
def test_user_agent_header_contains_version():
    """Verify that the User-Agent header contains the package version."""
    import importlib.metadata
    expected_version = importlib.metadata.version('cortexapps_cli')
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/catalog", json={"entities": [], "total": 0, "page": 0, "totalPages": 0}, status=200)
    cli(["catalog", "list", "-p", "0"])
    user_agent = responses.calls[0].request.headers.get("User-Agent", "")
    assert user_agent == f"cortexapps-cli/{expected_version}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `poetry run pytest tests/test_user_agent.py -v`
Expected: FAIL — User-Agent will be the default `python-requests/x.y.z`, not `cortexapps-cli/...`

- [ ] **Step 3: Commit failing test**

```bash
git add tests/test_user_agent.py
git commit -m "feat: add failing test for User-Agent header"
```

---

### Task 4: Implement User-Agent Header

**Files:**
- Modify: `cortexapps_cli/cortex_client.py:1` (add import)
- Modify: `cortexapps_cli/cortex_client.py:68-71` (add version resolution in `__init__`)
- Modify: `cortexapps_cli/cortex_client.py:110-114` (add header in `request`)

- [ ] **Step 1: Add import at top of cortex_client.py**

Add `import importlib.metadata` to the imports section.

- [ ] **Step 2: Add version resolution in `__init__()`**

After `self.base_url = base_url` (line 72), add:

```python
try:
    self.version = importlib.metadata.version('cortexapps_cli')
except importlib.metadata.PackageNotFoundError:
    self.version = 'unknown'
```

- [ ] **Step 3: Add User-Agent to request headers**

In `request()`, update `req_headers` to:

```python
req_headers = {
    'Authorization': f'Bearer {self.api_key}',
    'Content-Type': content_type,
    'User-Agent': f'cortexapps-cli/{self.version}',
    **headers
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `poetry run pytest tests/test_user_agent.py -v`
Expected: PASS — both tests green

- [ ] **Step 5: Commit implementation**

```bash
git add cortexapps_cli/cortex_client.py
git commit -m "feat: add User-Agent header to all CLI API requests"
```

---

### Task 5: Run Full Test Suite

- [ ] **Step 1: Run all tests**

Run: `just test-all`
Expected: All existing tests pass — the new header should not affect any existing behavior.

---

### Task 6: Create Pull Request

- [ ] **Step 1: Push branch and create PR to staging**

```bash
git push -u origin <issue-number>-user-agent-header
gh pr create --base staging --title "feat: Add User-Agent header to CLI API requests" --body "## Summary
- Adds User-Agent: cortexapps-cli/<version> header to all API requests
- Enables tracking CLI usage in DataDog via @user-agent:cortexapps-cli*
- Version resolved via importlib.metadata; falls back to 'unknown'

## Test plan
- [ ] Unit tests verify User-Agent header is set with correct format
- [ ] Full test suite passes
- [ ] Manual verification: run CLI command and confirm header appears in DataDog logs

Closes #<issue-number>"
```
