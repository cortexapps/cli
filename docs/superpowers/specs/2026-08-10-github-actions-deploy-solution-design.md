# GitHub Actions Deploy Solution Design

**Date:** 2026-08-10
**Linear:** [CX-6](https://linear.app/cortexio/issue/CX-6/deploys-github-actions)

## Overview

A Cortex solution that demonstrates deploy tracking via GitHub Actions. Serves both pre-sales (polished demo, end-to-end in minutes) and post-sales (real-world template customers adapt for production).

---

## Solution Structure

```
cortexapps_cli/solutions/github-actions-deploy/
├── README.md
├── catalog/
│   └── github-actions-demo.yaml
├── scorecards/
│   └── deploy-health.yaml
├── _templates/
│   └── cortex-deploy.yml             # GH Actions workflow seeded into user's repo
└── setup.py                          # Post-install setup script

cortexapps_cli/solutions/_lib/
└── setup_base.py                     # Shared SolutionSetup base class
```

### Key Conventions
- `_templates/` — files destined for a user's external repo, not their Cortex workspace
- `_lib/` — shared infrastructure not installed into Cortex
- Entity creation handled by backup import format (same as all other solutions)
- `setup.py` presence signals to `cortex solutions install` that post-install setup is available

---

## Entity: `github-actions-demo`

A standard service entity scoped to the demo via a group tag:

```yaml
openapi: "3.0.0"
info:
  title: GitHub Actions Demo
  x-cortex-tag: github-actions-demo
  x-cortex-type: service
  x-cortex-description: Sample service for demonstrating deploy tracking via GitHub Actions.
  x-cortex-definition: {}
  x-cortex-groups:
    - demo-github-actions-deploys
```

---

## GitHub Actions Workflow (`_templates/cortex-deploy.yml`)

Two jobs with explicit dependency — deploy notification only fires if build succeeds:

```yaml
on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Build
        run: echo "Hello, Cortex deploys!"

  notify-cortex:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Register deploy in Cortex
        run: |
          curl -s -X POST \
            "${{ secrets.CORTEX_BASE_URL }}/api/v1/catalog/github-actions-demo/deploys" \
            -H "Authorization: Bearer ${{ secrets.CORTEX_API_KEY }}" \
            -H "Content-Type: application/json" \
            -d '{
              "sha": "${{ github.sha }}",
              "environment": "production",
              "type": "DEPLOY",
              "title": "Triggered by ${{ github.actor }}",
              "deployer": { "name": "${{ github.actor }}" },
              "customData": {
                "branch": "${{ github.ref_name }}",
                "runId": "${{ github.run_id }}",
                "runUrl": "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}",
                "trigger": "${{ github.event_name }}"
              }
            }'
```

Two GitHub Actions secrets required: `CORTEX_API_KEY`, `CORTEX_BASE_URL`.

---

## Scorecard: Deploy Health

Scoped to the `demo-github-actions-deploys` group to avoid affecting existing services.

```yaml
tag: deploy-health
name: Deploy Health
description: Measures deployment cadence. Scoped to demo-github-actions-deploys group by default.
filter:
  kind: GENERIC
  types:
    include:
      - service
  query: hasGroup("demo-github-actions-deploys")
ladder:
  levels:
    - name: Bronze
      rank: 1
      color: "#CD7F32"
    - name: Silver
      rank: 2
      color: "#C0C0C0"
    - name: Gold
      rank: 3
      color: "#D7AC58"
rules:
  - title: Has at least one deploy
    expression: deploys().count() > 0
    level: Bronze

  - title: Deployed in the last 30 days
    expression: deploys(lookback=duration("P30D")).count() > 0
    level: Silver

  - title: Deployed in the last 7 days
    expression: deploys(lookback=duration("P7D")).count() > 0
    level: Gold
```

**Production note (in README):** Remove the group filter to apply the scorecard to all services. Customers can also add `demo-github-actions-deploys` to any existing service to opt it in.

---

## Setup Infrastructure

### Shared Base Class (`solutions/_lib/setup_base.py`)

```python
class SolutionSetup:
    def steps(self) -> list[tuple[str, callable]]:
        """Subclass returns ordered list of (label, fn) tuples."""
        ...

    def prompt(self, key, message, env_var=None, default=None, secret=False):
        """Prompt with env var fallback. Masks secrets. Caches answers."""
        ...

    def confirm(self, message) -> bool:
        """Y|N prompt, returns bool."""
        ...

    def already_done(self, key) -> bool:
        """Check idempotency state from ~/.cortex/setup-<solution>.json."""
        ...

    def mark_done(self, key):
        """Persist step completion to state file."""
        ...

    def run(self):
        """Collect prompts, then execute steps with progress display and error handling."""
        ...
```

State file: `~/.cortex/setup-<solution-tag>.json` — keyed per step, so re-runs skip completed steps and retry failed ones.

### Solution Setup Script (`github-actions-deploy/setup.py`)

Subclasses `SolutionSetup`. Prompts collected upfront:

```
GitHub token (or set GITHUB_TOKEN):        ********
GitHub org or username [<derived from token>]:
Repository name [cortex-deploy-demo]:
Cortex API key (or set CORTEX_API_KEY):    ********
Cortex base URL (or set CORTEX_BASE_URL):  https://api.getcortexapp.com
```

GitHub org/username defaults to the authenticated user derived via `GET https://api.github.com/user`. Supports org override for company repos.

Step execution:

```
[1/5] Creating GitHub repository...        ✓  (skips if already exists)
[2/5] Seeding Cortex deploy workflow...    ✓  (skips if already seeded)
[3/5] Setting CORTEX_API_KEY secret...     ✓
[4/5] Setting CORTEX_BASE_URL secret...    ✓

Ready to trigger your first workflow run? [Y/n]: Y
[5/5] Triggering workflow...               ✓

Done! Watch your first deploy appear at:
  https://<tenant>.getcortexapp.com/catalog/github-actions-demo
```

All steps are idempotent:
- Repo creation: `GET /repos/{owner}/{repo}` first, skip if 200
- Workflow seeding: check file SHA, skip if content unchanged
- Secrets: always safe to overwrite
- Workflow trigger: only on explicit Y confirmation

---

## CLI Integration

### `cortex solutions install`

After backup import completes, if a `setup.py` exists in the solution:

```
This solution includes a GitHub Actions setup script.
Configure GitHub Actions now? [Y/n]:
```

- **Y** → runs setup script
- **N** → prints: `Run setup later with: cortex solutions post-install -s github-actions-deploy`
- **`--skip-post-install-setup`** flag → skips prompt entirely, same "run later" note

### New: `cortex solutions post-install -s <solution>`

Invokes the solution's `setup.py` directly. Solutions without a `setup.py` return:
`No post-install setup available for this solution.`

---

## README (Solution Browser + Reference)

```markdown
---
name: GitHub Actions Deploy Tracking
description: Track deployments from GitHub Actions in Cortex, with a deploy health
             scorecard measuring delivery cadence.
---

## What's Included
- **Entity:** `github-actions-demo` service
- **Scorecard:** Deploy Health — Bronze/Silver/Gold based on deploy frequency
- **GitHub Actions workflow:** Two-job workflow (build → deploy notification)
- **Setup script:** Interactive wizard that creates and seeds a GitHub repo end-to-end

## Quick Start
1. Install the solution:
   cortex solutions install -s github-actions-deploy

2. Follow the post-install setup prompts, or run later:
   cortex solutions post-install -s github-actions-deploy

## How It Works
The included GitHub Actions workflow fires a deploy event to Cortex after every
successful build. The `notify-cortex` job only runs if the `build` job succeeds,
demonstrating conditional deploy tracking.

## Customizing for Production
- Point the workflow at your real entity by replacing `github-actions-demo` with your service tag
- Add `CORTEX_API_KEY` and `CORTEX_BASE_URL` secrets to your real repos
- The Deploy Health scorecard is scoped to `demo-github-actions-deploys` to avoid affecting
  your existing services. To roll it out broadly, remove the group filter from the scorecard.
  To opt in individual services, add the `demo-github-actions-deploys` group to them.
```

---

## What's Not In Scope

- No Cortex workflow (in-app) — the GitHub Actions workflow is the demo artifact
- No plugin/visualization — deploys surface natively in the Cortex entity page
- No custom entity type — uses standard `service` type for broad scorecard applicability
