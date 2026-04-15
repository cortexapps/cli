# Design: GitHub Workflow Action Block Functional Tests

**Date:** 2026-04-06
**Status:** Approved

## Overview

Functional tests for all 41 GitHub workflow action blocks in Cortex. Each test creates a one-step Cortex workflow that exercises a single GitHub action block, triggers it via the Cortex Workflows Run API, and verifies both the Cortex run status and the actual GitHub side-effect.

## Scope

### In scope
- 41 functional tests (one per GitHub action block)
- 41 workflow YAML definitions in `data/functional/workflows/`
- New CLI commands: `cortex workflows run`, `cortex workflows get-run`, `cortex workflows list-runs`
- Test infrastructure: fixtures, helpers, safeguards, sweep job
- Justfile recipes for running functional tests

### Out of scope
- LaunchDarkly API integration for dynamic feature flag management (deferred)
- Tests for non-GitHub workflow action blocks (future work)

## Prerequisites

### Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `CORTEX_API_KEY` | Yes | Existing — Cortex API auth |
| `CORTEX_BASE_URL` | Yes | Existing — Cortex API endpoint |
| `GITHUB_TEST_ORG` | Yes | Dedicated test GitHub org name |
| `GITHUB_TEST_PAT` | Yes | GitHub PAT with org admin + repo + team scopes |
| `GITHUB_TEST_USERNAME` | Yes | GitHub username for org/team membership tests |
| `LAUNCHDARKLY_API_KEY` | No | Future — dynamic feature flag management |

### External Prerequisites
- `gh` CLI installed and authenticated
- Test org has custom property `cortex-cli-functional-test = true`
- Cortex workflow run API feature flag enabled on the test tenant (`workflows.runWorkflowApi` in LaunchDarkly)
- Cortex API key has `Run workflows` and `View workflow runs` permissions

## Safeguards

Multiple layers of protection against accidental damage to non-test resources:

1. **Org safety marker**: Session fixture validates the org has custom property `cortex-cli-functional-test = true`. Entire suite aborts if missing.
2. **Resource naming prefix**: All created resources use `cli-functional-test-` prefix:
   - Repos: `cli-functional-test-{uuid8}`
   - Branches: `cli-functional-test-{test-name}`
   - Teams: `cli-functional-test-{test-name}`
   - Releases/tags: `cli-functional-test-v{n}`
   - PRs: titled with `[cli-functional-test]` prefix
3. **Repo custom property**: Every test repo gets `cli-functional-test-deletable = true`
4. **Cleanup scoping**: Teardown and sweep only delete resources matching the prefix. A `safe_delete()` helper validates the prefix before any delete operation.
5. **Env var gating**: `GITHUB_TEST_ORG` must be explicitly set. No default value.

### Sweep Job

A standalone cleanup script (`test_gh_sweep.py`) that can be run independently to clean up orphaned resources from interrupted test runs:
- Lists all repos in org with `cli-functional-test-deletable = true` property → deletes them
- Lists all teams matching `cli-functional-test-*` prefix → deletes them
- Runnable via `just test-functional-sweep`

## CLI Changes Required

Three new commands added to `cortex workflows`:

### `cortex workflows run`
Triggers a workflow run via `POST /api/v1/workflows/{tag}/runs`.

```
Options:
  -t, --tag        TEXT     Workflow tag [required]
  -s, --scope      TEXT     Scope type: GLOBAL or ENTITY [default: GLOBAL]
  -e, --entity     TEXT     Entity tag (required when scope is ENTITY)
  --run-as         TEXT     Email to run as
  --context        TEXT     JSON string for initialContext
  --context-file   FILE     JSON file for initialContext
  --wait           BOOL     Poll until run completes [default: false]
  --timeout        INT      Max seconds to wait when --wait is used [default: 300]
```

### `cortex workflows get-run`
Gets run details via `GET /api/v1/workflows/{tag}/runs/{runId}`.

```
Options:
  -t, --tag        TEXT     Workflow tag [required]
  -r, --run-id     TEXT     Run ID [required]
```

### `cortex workflows list-runs`
Lists runs via `GET /api/v1/workflows/runs`.

```
Options:
  -t, --tag        TEXT     Filter by workflow tag(s) [multiple allowed]
  -e, --entity     TEXT     Filter by entity tag
  --started-after  TEXT     ISO datetime filter
  --started-before TEXT     ISO datetime filter
  (plus standard ListCommandOptions: --table, --csv, --columns, --filter, --sort, --page, --page-size)
```

## Workflow YAML Structure

Each of the 41 action blocks gets a single-step workflow YAML in `data/functional/workflows/`.

**Naming convention:** `gh-{action-slug}.yaml`

**Template (ADVANCED_HTTP_REQUEST actions — 40 of 41):**
```yaml
name: "Functional Test: {Action Title}"
tag: func-test-gh-{action-slug}
description: Functional test for the {actionIdentifier} action block
isDraft: false
isRunnableViaApi: true
filter:
  type: GLOBAL
actions:
- name: {Action Title}
  slug: {action-slug}
  schema:
    type: ADVANCED_HTTP_REQUEST
    actionIdentifier: {github.actionId}
    integrationAlias: null
    inputs:
      {key}: "{{context.initialContext.{key}}}"
  outgoingActions: []
  isRootAction: true
```

**Template (GITHUB_CREATE_OR_UPDATE_FILE — 1 of 41):**

The "Create or update file" action uses a dedicated schema type, not the generic ADVANCED_HTTP_REQUEST pattern:
```yaml
name: "Functional Test: Create or update file"
tag: func-test-gh-create-or-update-file
description: Functional test for the GitHub create or update file action block
isDraft: false
isRunnableViaApi: true
filter:
  type: GLOBAL
actions:
- name: Create or update file
  slug: create-or-update-file
  schema:
    type: GITHUB_CREATE_OR_UPDATE_FILE
    alias: null
    repositoryName: "{{context.initialContext.repo}}"
    commitMessage: "{{context.initialContext.commit_message}}"
    content: "{{context.initialContext.content}}"
    path: "{{context.initialContext.path}}"
    branch: "{{context.initialContext.branch}}"
    committer: null
    author: null
  outgoingActions: []
  isRootAction: true
```

Runtime values (repo name, branch name, etc.) are injected via the `initialContext` field in the run request.

**Note on `integrationAlias`:** Setting `integrationAlias: null` uses the default GitHub integration configured on the tenant. If the test tenant has multiple GitHub integrations, a specific alias may need to be configured via an env var (e.g., `GITHUB_INTEGRATION_ALIAS`).

## Test Architecture

**Approach:** Fixture-per-test — each test is fully independent with its own fixture chain.

### File Structure

```
tests/functional/
  conftest.py                     # Session fixtures
  gh_helpers.py                   # GitHub helper functions
  test_functional_import.py       # Import functional test data
  test_gh_branches.py             # 7 tests
  test_gh_pull_requests.py        # 3 tests
  test_gh_repos.py                # 3 tests
  test_gh_releases.py             # 3 tests
  test_gh_deployments.py          # 3 tests
  test_gh_teams.py                # 8 tests (5 team + 3 membership)
  test_gh_org_members.py          # 3 tests
  test_gh_files.py                # 4 tests
  test_gh_branch_protection.py    # 3 tests
  test_gh_commits.py              # 2 tests
  test_gh_custom_properties.py    # 1 test
  test_gh_workflow_dispatch.py    # 1 test
  test_gh_sweep.py                # Standalone cleanup
```

### Session Fixtures (conftest.py)

Created once per test run, shared by all tests:

- `gh_test_org` — validates org exists and has safety marker
- `gh_test_repo` — creates ephemeral repo `cli-functional-test-{uuid8}` with README, sets `cli-functional-test-deletable = true`, deletes on teardown
- `gh_default_sha` — gets HEAD commit SHA of default branch
- `import_functional_workflows` — imports all 41 workflow YAMLs via `cortex backup import`

### Per-Test Fixtures

Each test creates its own precondition resources (branches, PRs, teams, etc.) with unique names to avoid collisions. Cleanup happens in fixture teardown.

### Test Pattern

```python
@pytest.mark.functional
def test_gh_create_branch(gh_test_repo, gh_default_sha, import_functional_workflows):
    # 1. Trigger: cortex workflows run -t func-test-gh-create-branch --context '...' --wait
    # 2. Assert Cortex run status == completed
    # 3. Verify: gh api /repos/{repo}/branches/{branch} returns 200
```

### Helper Functions (gh_helpers.py)

- `gh_api(method, path, **kwargs)` — wrapper around `gh api`
- `safe_delete_repo(repo)` — validates `cli-functional-test-` prefix before deleting
- `safe_delete_team(org, slug)` — validates prefix before deleting
- `wait_for_workflow_run(tag, run_id, timeout=60)` — polls Cortex run status
- `run_workflow(tag, initial_context)` — triggers workflow via CLI, returns run details

## Complete Test Matrix (41 tests)

### Branch Operations (test_gh_branches.py — 7 tests)

| # | Action Block | Action ID | Precondition | Verification |
|---|-------------|-----------|-------------|--------------|
| 1 | Create a branch | github.createBranch | default SHA | branch exists |
| 2 | Get a branch | github.getBranch | create branch | response has branch details |
| 3 | List branches | github.listBranches | none | response has branch list |
| 4 | Rename a branch | github.renameBranch | create branch | old gone, new exists |
| 5 | Merge a branch | github.mergeBranch | create branch + commit | merge commit on target |
| 6 | Delete a branch | github.deleteBranch | create branch | branch gone |
| 7 | Create reference | github.createReference | default SHA | ref exists |

### Pull Request Operations (test_gh_pull_requests.py — 3 tests)

| # | Action Block | Action ID | Precondition | Verification |
|---|-------------|-----------|-------------|--------------|
| 8 | Create pull request | github.createPullRequest | branch with commit | PR exists |
| 9 | Create PR comment | github.createPullRequestComment | create PR | comment exists |
| 10 | Add label to PR | github.addLabelToPullRequest | create PR | label present |

### Repository Operations (test_gh_repos.py — 3 tests)

| # | Action Block | Action ID | Precondition | Verification |
|---|-------------|-----------|-------------|--------------|
| 11 | Create repository | github.createRepository | none | repo exists with deletable property |
| 12 | Update repository | github.updateRepository | create repo | settings changed |
| 13 | List repositories | github.listRepositories | none | response has repos |

### Release Operations (test_gh_releases.py — 3 tests)

| # | Action Block | Action ID | Precondition | Verification |
|---|-------------|-----------|-------------|--------------|
| 14 | Create release | github.createRelease | create tag | release exists |
| 15 | Get release by tag | github.getReleaseByTag | create release | response has details |
| 16 | List releases | github.listReleases | create release | response has list |

### Deployment Operations (test_gh_deployments.py — 3 tests)

| # | Action Block | Action ID | Precondition | Verification |
|---|-------------|-----------|-------------|--------------|
| 17 | Create deployment | github.createDeployment | none (default ref) | deployment exists |
| 18 | Get deployment | github.getDeployment | create deployment | response has details |
| 19 | List deployments | github.listDeployments | create deployment | response has list |

### Team Operations (test_gh_teams.py — 8 tests)

| # | Action Block | Action ID | Precondition | Verification |
|---|-------------|-----------|-------------|--------------|
| 20 | Create team | github.createTeam | none | team exists |
| 21 | Get team | github.getTeam | create team | response has details |
| 22 | List teams | github.listTeams | none | response has list |
| 23 | List team members | github.listTeamMembers | team + member | response has members |
| 24 | Delete team | github.deleteTeam | create team | team gone |
| 25 | Add user to team | github.addUserToTeam | create team | membership confirmed |
| 26 | Get team membership | github.getTeamMembership | add user | response has membership |
| 27 | Remove user from team | github.removeUserFromTeam | add user | membership gone |

### Org Member Operations (test_gh_org_members.py — 3 tests)

| # | Action Block | Action ID | Precondition | Verification |
|---|-------------|-----------|-------------|--------------|
| 28 | Add user to org | github.addUserToOrg | none | user in org |
| 29 | List org members | github.listOrgMembers | none | response has members |
| 30 | Remove user from org | github.removeUserFromOrg | add user | user removed |

### File Operations (test_gh_files.py — 4 tests)

| # | Action Block | Action ID | Precondition | Verification |
|---|-------------|-----------|-------------|--------------|
| 31 | Create or update file | GITHUB_CREATE_OR_UPDATE_FILE (dedicated type) | none | file exists |
| 32 | Get file | github.getFile | create file | response has content |
| 33 | Find files | github.findFile | create file | file in results |
| 34 | Delete file | github.deleteFile | create file + get SHA | file gone |

### Branch Protection Operations (test_gh_branch_protection.py — 3 tests)

| # | Action Block | Action ID | Precondition | Verification |
|---|-------------|-----------|-------------|--------------|
| 35 | Update branch protection | github.updateBranchProtectionRules | none (default branch) | rules set |
| 36 | Get branch protection | github.getBranchProtectionRules | set rules | response has rules |
| 37 | Delete branch protection | github.deleteBranchProtectionRules | set rules | rules removed |

### Commit Operations (test_gh_commits.py — 2 tests)

| # | Action Block | Action ID | Precondition | Verification |
|---|-------------|-----------|-------------|--------------|
| 38 | Get commit | github.getCommit | none (initial commit) | response has details |
| 39 | List commits | github.listCommits | none | response has list |

### Custom Properties (test_gh_custom_properties.py — 1 test)

| # | Action Block | Action ID | Precondition | Verification |
|---|-------------|-----------|-------------|--------------|
| 40 | Create/update custom properties | github.createOrUpdateCustomPropertyValues | none | property set |

### Workflow Dispatch (test_gh_workflow_dispatch.py — 1 test)

| # | Action Block | Action ID | Precondition | Verification |
|---|-------------|-----------|-------------|--------------|
| 41 | Trigger workflow | github.createWorkflowDispatchEvent | create .github/workflows/test.yml | GH Actions run appears |

## Execution

### Justfile Recipes

```just
# Run functional tests (serially by default; add -n auto for parallel)
test-functional: test-functional-import
   {{pytest}} -v -s -m functional --html=report-functional.html --self-contained-html tests/functional/

# Import functional test data
test-functional-import:
   {{pytest}} tests/functional/test_functional_import.py --cov=cortexapps_cli --cov-report=

# Clean up orphaned test resources
test-functional-sweep:
   {{pytest}} -v -s tests/functional/test_gh_sweep.py
```

### Running Locally

```bash
# Set env vars
export GITHUB_TEST_ORG=your-test-org
export GITHUB_TEST_PAT=ghp_...
export GITHUB_TEST_USERNAME=test-user

# Run all functional tests serially
just test-functional

# Run a single test file
just test tests/functional/test_gh_branches.py

# Clean up orphaned resources
just test-functional-sweep
```

Functional tests are excluded from `just test-all` via the `functional` pytest marker and default `addopts` in `pytest.ini`.

### Parallelism

Tests start serial (no `-n auto`). Once stable, parallelism can be enabled since each test uses unique resource names. GitHub rate limits (5000 req/hr) are sufficient for 41 tests.

## Implementation Order

1. Create GH issue and feature branch for CLI workflow run commands
2. Implement `cortex workflows run`, `get-run`, `list-runs`
3. Create `data/functional/workflows/` with all 41 workflow YAMLs
4. Build test infrastructure: `conftest.py`, `gh_helpers.py`
5. Implement tests by group (branches first, then PRs, etc.)
6. Add Justfile recipes
7. Create sweep job
8. Manual local testing before any commits
