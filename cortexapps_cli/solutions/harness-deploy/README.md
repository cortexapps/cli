---
name: Harness Deploy Tracking
description: Track deployments from Harness pipelines in Cortex, with a deploy health scorecard measuring delivery cadence.
---

# Harness Deploy Tracking

Trigger deploys from Cortex, track them as they run in Harness, and surface deploy health back in your service catalog.

```
  ┌─────────────────────────────────┐
  │         Cortex Catalog          │
  │                                 │
  │    harness-demo  (service)      │
  │    └── Scorecard: Deploy Health │
  │          Bronze / Silver / Gold │
  └──────────────┬──────────────────┘
                 │
                 │  Run workflow from entity page
                 │  (or: cortex workflows run -t
                 │   harness-trigger-deploy
                 │   --scope ENTITY --entity <tag>)
                 ▼
  ┌─────────────────────────────────┐
  │       Cortex Workflow           │
  │    Trigger Harness Deploy       │
  │                                 │
  │  1. Read Harness config from    │
  │     entity custom metadata      │
  │  2. POST /execute to Harness    │
  │     pipeline via integration    │
  │  3. Pass callback URL as        │
  │     pipeline variable           │
  │  4. Wait for callback           │
  └──────────────┬──────────────────┘
                 │  POST /execute  (Harness integration)
                 ▼
  ┌─────────────────────────────────┐
  │         Harness Pipeline        │
  │         cortex-deploy           │
  │                                 │
  │  stage: Build                   │
  │    └── run your deploy steps    │
  │                                 │
  │  stage: Record Deploy in Cortex │
  │    └── POST /deploys       ◄────┼── registers deploy event
  │        (entity: harness-demo)   │   on the Cortex entity
  │                                 │
  │  stage: Callback to Cortex      │
  │    └── POST callbackUrl ───────►│   Cortex marks workflow
  │        status: SUCCESS/FAILURE  │   run complete
  └─────────────────────────────────┘
```

## What's Included

- **Entity:** `harness-demo` service — a sample entity to receive deploy events
- **Scorecard:** Deploy Health — Bronze/Silver/Gold based on deploy frequency
- **Harness stage templates:** `cortex_record_deploy` and `cortex_async_callback` — reusable Stage Templates that register the deploy event and call back to Cortex; reference them from any pipeline
- **Harness pipeline:** `cortex-deploy` — a three-stage demo pipeline (Build → Record Deploy in Cortex → Callback to Cortex) created in your Harness project
- **Cortex workflow:** `harness-trigger-deploy` — reads Harness coordinates from entity custom metadata, triggers the pipeline via the Harness integration, and waits for the result
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

The Cortex workflow triggers `cortex-deploy` via the Harness integration, passing a `callback_url` as a pipeline variable. Cortex waits asynchronously for the pipeline to report back.

Harness runs the build, then notifies Cortex twice on completion:
- **Deploy registration** (`POST /api/v1/catalog/{tag}/deploys`) — records the deploy event on the entity, feeding the Deploy Health scorecard
- **Workflow callback** — signals the Cortex workflow run as SUCCESS or FAILURE

## After Installing

If you ran the post-install setup, you're already done — it configured the Harness integration, created the pipeline and `cortex_api_key` secret in Harness, imported the Cortex workflow, and triggered a test deploy.

To roll the pattern out to your own services:

1. Add both **Cortex Record Deploy** and **Cortex Async Callback** stage templates to any existing Harness pipeline (each needs only the `cortex_api_key` secret and its one pipeline variable)

2. Add a `x-cortex-custom-metadata` block to your entity's catalog YAML with your Harness coordinates:

   ```yaml
   x-cortex-custom-metadata:
     harness:
       org: your-org
       project: your-project
       pipeline: your-pipeline-id
   ```

3. Run the **Solution: Trigger Harness Deploy** workflow from the entity page — it reads the Harness coordinates from the entity's custom metadata automatically, with no manual inputs required

> **Note:** The custom metadata approach is a stand-in for a native Harness integration that is in development. Once released, Harness coordinates will likely be read directly from the integration config rather than custom metadata.

## Customizing for Production

- Point the workflow at your real entity by replacing `harness-demo` with your service tag
- Add the `cortex_api_key` secret to your real Harness projects
- The Deploy Health scorecard is scoped to `demo-harness-deploys` to avoid affecting your existing services. To roll it out broadly, remove the group filter from the scorecard. To opt in individual services, add the `demo-harness-deploys` group to them.
