# Functional Tests: GitHub Workflow Action Blocks

These tests exercise Cortex GitHub workflow action blocks end-to-end: import a workflow into Cortex, trigger it via the API, and verify the GitHub side-effect.

## Prerequisites

### 1. GitHub Test Organization

You need a dedicated GitHub org for testing. **Do not use a production org.**

Create a free GitHub org (e.g., `my-cortex-test-org`) and add a custom property to mark it as safe for testing:

1. Go to your org's **Settings > Custom properties**
2. Create a new property:
   - Name: `cortex-cli-functional-test`
   - Type: True/False (or String)
3. Set the value — its mere existence is the safety check

This prevents the tests from accidentally running against a production org.

### 2. GitHub Personal Access Token (PAT)

Create a **fine-grained PAT** or **classic PAT** with these scopes:

**Classic PAT scopes:**
- `repo` (full control of private repositories)
- `admin:org` (manage orgs, teams, members)
- `delete_repo` (delete repositories)

**Fine-grained PAT permissions (on the test org):**
- Repository: Administration (read/write), Contents (read/write), Metadata (read)
- Organization: Members (read/write), Custom properties (read/write)

### 3. GitHub CLI (`gh`)

Install the GitHub CLI: https://cli.github.com/

```bash
# macOS
brew install gh

# Verify
gh --version
```

The tests use `gh api` with `GH_TOKEN` env var — you don't need to run `gh auth login`.

### 4. Cortex Tenant Configuration

Your Cortex test tenant needs:

- **GitHub integration configured** — the workflows use Cortex's GitHub integration to make API calls. The integration must have access to your test org.
- **Workflow Run API enabled** — the LaunchDarkly flag `workflows.runWorkflowApi` must be enabled for your tenant.
- **API key permissions** — your `CORTEX_API_KEY` must have `Run workflows` and `View workflow runs` permissions in addition to the standard permissions for the CLI tests.

### 5. Test User Account

Some tests (org membership, team membership) need a GitHub username to add/remove. This should be a real GitHub user who can accept org invitations, or a bot account in your test org.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `CORTEX_API_KEY` | Yes | Cortex API key (existing — same as CLI tests) |
| `CORTEX_BASE_URL` | Yes | Cortex API endpoint (existing — same as CLI tests) |
| `GITHUB_TEST_ORG` | Yes | Your dedicated test GitHub org name |
| `GITHUB_TEST_PAT` | Yes | GitHub PAT with the scopes listed above |
| `GITHUB_TEST_USERNAME` | Yes | GitHub username for membership tests |
| `GITHUB_INTEGRATION_ALIAS` | Yes | Cortex GitHub integration alias (find in Settings > Integrations > GitHub) |

Example `.env` setup (do NOT commit this file):

```bash
export CORTEX_API_KEY=your-cortex-api-key
export CORTEX_BASE_URL=https://api.getcortexapp.com
export GITHUB_TEST_ORG=my-cortex-test-org
export GITHUB_TEST_PAT=ghp_xxxxxxxxxxxxxxxxxxxx
export GITHUB_TEST_USERNAME=some-github-user
export GITHUB_INTEGRATION_ALIAS=your-github-integration-alias
```

## Running the Tests

```bash
# Source your env vars
source .env  # or however you manage secrets

# Import functional test data (workflow YAMLs) into Cortex
just test-functional-import

# Run all functional tests
just test-functional

# Run a single test file
just test tests/functional/test_gh_branches.py

# Run directly with pytest (bypasses Justfile env checks)
PYTHONPATH=. poetry run pytest -rA -v -s -m functional tests/functional/test_gh_branches.py

# Clean up orphaned test resources from interrupted runs
just test-functional-sweep
```

## What the Tests Do

Each test:
1. **Setup** (session fixture): Validates the test org safety marker, creates an ephemeral repo (`cli-functional-test-{uuid}`), imports workflow YAMLs
2. **Execute**: Triggers a Cortex workflow via `cortex workflows run`, which calls the GitHub API through Cortex's integration
3. **Verify**: Checks the Cortex workflow run status AND verifies the GitHub side-effect via `gh api`
4. **Teardown** (session fixture): Deletes the ephemeral repo

## Safety

- Tests **will not run** if `GITHUB_TEST_ORG` is not set (Justfile checks)
- Tests **abort** if the org doesn't have the `cortex-cli-functional-test` custom property
- All created resources use the `cli-functional-test-` prefix
- Cleanup only deletes resources matching that prefix
- Repos get the `cortex-cli-functional-test = true` custom property (required by org policy, also used for sweep identification)

## Troubleshooting

**`ERROR: GITHUB_TEST_ORG is not set`** — Set the required env vars (see above).

**`Org 'X' does not have custom property 'cortex-cli-functional-test'`** — Create the custom property in your test org's Settings.

**`HTTP Error 403: Running a workflow is not enabled`** — The LaunchDarkly flag `workflows.runWorkflowApi` needs to be enabled for your Cortex tenant.

**Workflow run status is FAILED** — Check the workflow run details in the Cortex UI. Common issues: GitHub integration not configured, PAT doesn't have required scopes, repo doesn't exist.

**Orphaned test resources** — If a test run is interrupted, repos/teams may be left behind. Run `just test-functional-sweep` to clean them up.
