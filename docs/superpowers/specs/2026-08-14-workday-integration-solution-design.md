# Workday Integration Solution Design

> **Status:** Approved

## Goal

Add a `workday-integration` Cortex CLI solution that configures the Cortex Workday integration to sync a Pied Piper org hierarchy from a public JSON report bundled in the CLI repo.

## Architecture

A minimal solution: bundled static data + a `configuration.json` field mapping + a lightweight setup wizard that makes one Cortex API call. No external services to create, no scorecards, no entity types to install. The Workday integration in Cortex handles entity creation when the user triggers the sync.

## Tech Stack

- Python 3.11+, `requests`, `SolutionSetup` base class (same pattern as `github-actions-deploy`)
- Data served via `raw.githubusercontent.com` (no GitHub Pages setup required)

## Global Constraints

- Solution tag: `workday-integration`
- Data file: `ONE_EMPLOYEE_ONE_TEAM` hierarchy format
- Report URL: `https://raw.githubusercontent.com/cortexapps/cli/main/cortexapps_cli/solutions/workday-integration/data/pied-piper-hierarchy.json`
- No scorecards, no catalog entity imports, no entity types
- `SolutionSetup` base class must be imported dynamically (same pattern as `github-actions-deploy/setup.py`)
- State file lives at `~/.cortex/solutions/workday-integration.json`

---

## File Structure

```
cortexapps_cli/solutions/workday-integration/
├── README.md
├── setup.py
└── data/
    ├── pied-piper-hierarchy.json     # Pied Piper org report (copied from workday-mocks)
    └── configuration.json            # Cortex Workday integration config (static, bundled)
```

---

## Data

### `data/pied-piper-hierarchy.json`

Copied verbatim from `~/git/jeff-test-org/workday-mocks/pied-piper-hierarchy/index.json`.

`ONE_EMPLOYEE_ONE_TEAM` format. Each entry has: `email`, `employeeId`, `firstName`, `lastName`, `managersEmail`, `teamId`, `teamName`, `parentTeamId`. Root employee self-references in `managersEmail`. Root teams have `parentTeamId: "NONE"`.

### `data/configuration.json`

Static — the URL is fixed at the raw.githubusercontent.com path above.

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

---

## Setup Script (`setup.py`)

Extends `SolutionSetup`. No prompts for credentials — the CLI already has them via `ctx`. Zero prompts in `collect_prompts()`.

Credentials are read from `ctx.obj["client"]` (the `CortexClient` already configured for the session): `client.api_key` and `client.base_url`.

### `collect_prompts()`

Empty — no user prompts needed.

### `steps()`

**Step 1: Check for existing Workday integration**
- `GET {base_url}/api/v1/integrations/workday`
- If 404: no existing config, proceed to Step 2
- If 200: existing integration found — prompt: `"Existing Workday integration found. Replace it? [y/N]"`
  - If N: abort with message `"Keeping existing Workday integration. Exiting."`
  - If Y:
    - Write existing config response body to `~/.cortex/solutions/workday-integration/backup-config.json`
    - `DELETE {base_url}/api/v1/integrations/workday`

**Step 2: Configure Workday integration**
- Reads `data/configuration.json` from the solution directory
- `POST {base_url}/api/v1/integrations/workday` with config as JSON body
- Auth header: `Authorization: Bearer {api_key}`
- On success: prints confirmation
- On error: raises with response body for diagnosis

Uses `already_done` / `mark_done` for idempotency (re-running post-install skips Step 2 if already done).

### `post_steps()`

Prints:

```
✓ Workday integration configured with the Pied Piper org hierarchy.

Next: trigger the import in Cortex:
  Catalog → All Entities → Import Entities

Then check your team hierarchy to see the Pied Piper org chart.
```

---

## README.md

Covers:
- What the solution installs (integration config + Pied Piper data)
- Quick start (`cortex solutions install -s workday-integration`)
- How to trigger the sync (Catalog → All Entities → Import Entities)
- What to expect after sync (employees + team hierarchy in Cortex)
- How to adapt to real Workday data (swap `ownershipReportUrl`, set real `username`/`password`)

---

## Testing

- Unit tests for `setup.py`: mock the `requests.post` call, verify correct URL + payload
- Integration test: `cortex solutions post-install -s workday-integration --no-prompt` against a sandbox tenant
