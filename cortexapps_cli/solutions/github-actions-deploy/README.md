---
name: GitHub Actions Deploy Tracking
description: Track deployments from GitHub Actions in Cortex, with a deploy health scorecard measuring delivery cadence.
---

## What's Included

- **Entity:** `github-actions-demo` service — a sample entity to receive deploy events
- **Scorecard:** Deploy Health — Bronze/Silver/Gold based on deploy frequency
- **GitHub Actions workflow:** A two-job workflow (build → deploy notification) to seed into a GitHub repo
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

The included GitHub Actions workflow fires a deploy event to Cortex after every successful build.
The `notify-cortex` job only runs if the `build` job succeeds, demonstrating conditional deploy tracking.

## Customizing for Production

- Point the workflow at your real entity by replacing `github-actions-demo` with your service tag
- Add `CORTEX_API_KEY` and `CORTEX_BASE_URL` secrets to your real repos
- The Deploy Health scorecard is scoped to `demo-github-actions-deploys` to avoid affecting your
  existing services. To roll it out broadly, remove the group filter from the scorecard.
  To opt in individual services, add the `demo-github-actions-deploys` group to them.
