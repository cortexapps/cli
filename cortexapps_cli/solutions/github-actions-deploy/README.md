---
name: GitHub Actions Deploy Tracking
description: Track deployments from GitHub Actions in Cortex, with a deploy health scorecard measuring delivery cadence.
---

## What's Included

- **Entity:** `github-actions-demo` service — a sample entity to receive deploy events
- **Scorecard:** Deploy Health — Bronze/Silver/Gold based on deploy frequency
- **GitHub Actions workflow:** A two-job workflow (build → deploy notification) to seed into a GitHub repo
- **Setup script:** Interactive wizard that creates and seeds a GitHub repo end-to-end
- **Cortex workflow — Deploy from Entity** _(recommended)_: triggers a GitHub Actions deploy directly from any entity that has a linked GitHub repository — no manual input required
- **Cortex workflow — Trigger GitHub Actions Deploy**: triggers a deploy by supplying the GitHub owner and repo name explicitly; handles both UI and API invocation via a branch + variables pattern

## Quick Start

1. Install the solution:

   ```
   cortex solutions install -s github-actions-deploy
   ```

2. Follow the post-install setup prompts, or run later:

   ```
   cortex solutions post-install -s github-actions-deploy
   ```

## Cortex Workflows

Two Cortex workflows are included. Both trigger the same GitHub Actions deploy and wait for a callback, but differ in how the target repository is resolved.

### Deploy from Entity _(recommended)_

Reads the GitHub repository directly from the entity's catalog configuration — no user input needed. Run it from any entity that has a `x-cortex-git.github.repository` set.

Use this workflow for day-to-day deploys. It will likely replace the trigger workflow below once entity-linked repos are the standard pattern.

### Trigger GitHub Actions Deploy

Prompts for a GitHub owner and repository name when triggered from the UI, or accepts them as variables when triggered via API. This workflow is a good reference example of:

- **Variables + branch pattern**: a `CONDITIONAL_BRANCH` routes UI invocations through a `USER_INPUT` step to collect the owner and repo, while API invocations skip it entirely and pass through to the same merge point
- **SET_VARIABLES**: copies `USER_INPUT` outputs into workflow variables so they're available to later steps regardless of which path was taken

## How It Works

The included GitHub Actions workflow fires a deploy event to Cortex after every successful build.
The `notify-cortex` job only runs if the `build` job succeeds, demonstrating conditional deploy tracking.

## Customizing for Production

- Point the workflow at your real entity by replacing `github-actions-demo` with your service tag
- Add `CORTEX_API_KEY` and `CORTEX_BASE_URL` secrets to your real repos
- The Deploy Health scorecard is scoped to `demo-github-actions-deploys` to avoid affecting your
  existing services. To roll it out broadly, remove the group filter from the scorecard.
  To opt in individual services, add the `demo-github-actions-deploys` group to them.
