---
name: Harness Deploy Tracking
description: Track deployments from Harness pipelines in Cortex, with a deploy health scorecard measuring delivery cadence.
---

## What's Included

- **Entity:** `harness-demo` service — a sample entity to receive deploy events
- **Scorecard:** Deploy Health — Bronze/Silver/Gold based on deploy frequency
- **Harness pipeline:** A sample pipeline YAML (with callback + deploy registration) to import into Harness
- **Cortex workflow:** Async trigger that fires a Harness pipeline and waits for it to report back
- **Setup script:** Interactive wizard that wires everything together end-to-end

## Quick Start

1. Install the solution:

   ```
   cortex solutions install -s harness-deploy
   ```

2. Follow the post-install setup prompts, or run later:

   ```
   cortex solutions post-install -s harness-deploy
   ```

## How It Works

The included Harness pipeline YAML registers a deploy event to Cortex after each run and calls back
to the Cortex async workflow to surface the result directly in the Cortex UI.

## Customizing for Production

- Point the workflow at your real entity by replacing `harness-demo` with your service tag in the
  pipeline's `CORTEX_ENTITY_TAG` variable
- Add `CORTEX_API_KEY` and `CORTEX_BASE_URL` as Harness pipeline variables or secrets
- The Deploy Health scorecard is scoped to `demo-harness-deploys` to avoid affecting your existing
  services. To roll it out broadly, remove the group filter. To opt in individual services, add the
  `demo-harness-deploys` group to them.
