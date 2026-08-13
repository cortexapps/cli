---
name: GitHub Actions Deploy Tracking
description: Track deployments from GitHub Actions in Cortex, with a deploy health scorecard measuring delivery cadence.
---

# GitHub Actions Deploy Tracking

Trigger deploys from Cortex, track them as they run in GitHub Actions, and surface deploy health back in your service catalog.

```
  ┌─────────────────────────────────┐
  │         Cortex Catalog          │
  │                                 │
  │  github-actions-demo  (service) │
  │  ├── x-cortex-git.github        │
  │  │     repository: owner/repo   │
  │  └── Scorecard: Deploy Health   │
  │        Bronze / Silver / Gold   │
  └──────────────┬──────────────────┘
                 │
                 │  Run workflow from entity page
                 │  (or: cortex workflows run -t
                 │   github-actions-deploy
                 │   --scope ENTITY --entity <tag>)
                 ▼
  ┌─────────────────────────────────┐
  │       Cortex Workflow           │
  │  Solution: Add Cortex Deploy    │
  │       from GitHub Actions       │
  │                                 │
  │  1. Read linked repo from       │
  │     entity catalog config       │
  │  2. POST workflow_dispatch      │
  │     to GitHub Actions           │
  │  3. Wait for callback           │
  └──────────────┬──────────────────┘
                 │  POST /dispatches  (GitHub integration)
                 ▼
  ┌─────────────────────────────────┐
  │        GitHub Actions           │
  │    cortex-deploy.yml            │
  │                                 │
  │  job: build                     │
  │    └── run your deploy steps    │
  │                                 │
  │  job: notify-cortex             │
  │    ├── POST /deploys            │◄── registers deploy event
  │    │   (entity: github-actions- │    on the Cortex entity
  │    │    demo)                   │
  │    └── POST callbackUrl  ───────┼──► Cortex marks workflow
  │        status: SUCCESS/FAILURE  │    run complete
  └─────────────────────────────────┘
```

## What's Included

- **Entity:** `github-actions-demo` service — a sample entity to receive deploy events
- **Scorecard:** Deploy Health — Bronze/Silver/Gold based on deploy frequency
- **GitHub Actions workflow:** `cortex-deploy.yml` — a two-job workflow (build → notify) seeded into your GitHub repo
- **Cortex workflow:** `github-actions-deploy` — reads the linked repo from the entity, triggers the GitHub Actions deploy, and waits for the result
- **Setup script:** Interactive wizard that creates and seeds a GitHub repo end-to-end

## Quick Start

1. Install the solution:

   ```
   cortex solutions install -s github-actions-deploy
   ```

2. Follow the post-install setup prompts, or run later:

   ```
   cortex solutions post-install -s github-actions-deploy
   ```

## How It Works

The Cortex workflow reads `x-cortex-git.github.repository` from the entity's catalog config to determine which GitHub repo to deploy. It triggers `cortex-deploy.yml` via `workflow_dispatch` and waits asynchronously for a callback.

GitHub Actions runs the build, then notifies Cortex twice on completion:
- **Deploy registration** (`POST /api/v1/catalog/{tag}/deploys`) — records the deploy event on the entity, feeding the Deploy Health scorecard
- **Workflow callback** — signals the Cortex workflow run as SUCCESS or FAILURE

## Customizing for Production

- Point the workflow at your real entity by replacing `github-actions-demo` with your service tag
- Add `CORTEX_API_KEY` and `CORTEX_BASE_URL` secrets to your real repos
- The Deploy Health scorecard is scoped to `demo-github-actions-deploys` to avoid affecting your
  existing services. To roll it out broadly, remove the group filter from the scorecard.
  To opt in individual services, add the `demo-github-actions-deploys` group to them.
