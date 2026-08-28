---
name: Jenkins Deploy Tracking
description: Track deployments from Jenkins pipelines in Cortex, with a deploy health scorecard measuring delivery cadence.
---

# Jenkins Deploy Tracking

Trigger deploys from Cortex, track them as they run in Jenkins, and surface deploy health back in your service catalog.

```
  ┌─────────────────────────────────┐
  │         Cortex Catalog          │
  │                                 │
  │    jenkins-demo  (service)      │
  │    ├── x-cortex-custom-metadata │
  │    │     jenkins:               │
  │    │       url / job            │
  │    └── Scorecard: Deploy Health │
  │          Bronze / Silver / Gold │
  └──────────────┬──────────────────┘
                 │
                 │  Run workflow from entity page
                 │  (or: cortex workflows run -t
                 │   jenkins-trigger-deploy
                 │   --scope ENTITY --entity <tag>)
                 ▼
  ┌─────────────────────────────────┐
  │       Cortex Workflow           │
  │    Trigger Jenkins Deploy       │
  │                                 │
  │  1. Read Jenkins config from    │
  │     entity custom metadata      │
  │  2. POST /buildWithParameters   │
  │     to Jenkins via HTTP         │
  │  3. Pass callback URL as        │
  │     pipeline parameter          │
  │  4. Wait for callback           │
  └──────────────┬──────────────────┘
                 │  POST /buildWithParameters  (HTTP + Basic auth)
                 ▼
  ┌─────────────────────────────────────────────────────────┐
  │  GitHub Codespaces  (optional — provisioned by setup)   │
  │  port 8080 exposed publicly for demo                    │
  │                                                         │
  │  ┌─────────────────────────────────┐                    │
  │  │         Jenkins Pipeline        │                    │
  │  │         cortex-deploy           │                    │
  │  │                                 │                    │
  │  │  stage: Build                   │                    │
  │  │    └── run your deploy steps    │                    │
  │  │                                 │                    │
  │  │  stage: Record Deploy in Cortex │                    │
  │  │    └── POST /deploys       ◄────┼── registers deploy │
  │  │        (entity: jenkins-demo)   │   event on entity  │
  │  │                                 │                    │
  │  │  post { always }                │                    │
  │  │    └── POST callbackUrl ───────►│   Cortex marks     │
  │  │        status: SUCCESS/FAILURE  │   workflow done    │
  │  └─────────────────────────────────┘                    │
  └─────────────────────────────────────────────────────────┘
  (or point to your own Jenkins instance — Codespaces not required)
```

## What's Included

- **Entity:** `jenkins-demo` service — a sample entity to receive deploy events
- **Scorecard:** Deploy Health — Bronze/Silver/Gold based on deploy frequency
- **Jenkinsfile:** `cortex-deploy` — a two-stage pipeline (Build → Record Deploy) with an async callback to Cortex; drop it into any existing Jenkins job
- **Cortex workflow:** `jenkins-trigger-deploy` — reads Jenkins coordinates from entity custom metadata, triggers the pipeline via HTTP, and waits for the result
- **Setup script:** Interactive wizard that wires everything together end-to-end; optionally provisions Jenkins in GitHub Codespaces for a zero-install demo

## Quick Start

1. Install the solution:

   ```
   cortex solutions install -s jenkins-deploy
   ```

2. Follow the post-install setup prompts, or run later:

   ```
   cortex solutions post-install -s jenkins-deploy
   ```

## How It Works

The Cortex workflow reads Jenkins coordinates from `x-cortex-custom-metadata.jenkins` on the entity, then triggers `cortex-deploy` via `buildWithParameters`, passing a `callback_url` as a pipeline parameter. Cortex waits asynchronously for the pipeline to report back.

Jenkins runs the build, then notifies Cortex twice on completion:
- **Deploy registration** (`POST /api/v1/catalog/{tag}/deploys`) — records the deploy event on the entity, feeding the Deploy Health scorecard
- **Workflow callback** — signals the Cortex workflow run as SUCCESS or FAILURE

## After Installing

If you ran the post-install setup, you're already done — it created the Jenkins job, added credentials, wrote Jenkins coordinates to the entity's custom metadata, imported the Cortex workflow, and triggered a test deploy.

To roll the pattern out to your own services:

1. Add the `cortex-deploy` **Jenkinsfile** stages to any existing Jenkins pipeline (needs only `CORTEX_API_KEY` and `CORTEX_BASE_URL` secret-text credentials)

2. Add a `x-cortex-custom-metadata` block to your entity's catalog YAML with your Jenkins coordinates:

   ```yaml
   x-cortex-custom-metadata:
     jenkins:
       url: "https://jenkins.example.com"
       job: "your-pipeline-name"
   ```

3. If your Jenkins instance requires authentication, create a **Cortex secret** named `jenkins_auth` whose value is your Jenkins credentials base64-encoded:

   ```bash
   echo -n "your-username:your-api-token" | base64
   ```

   Then add an `Authorization` header to the **Trigger Jenkins Build** action in the imported workflow:

   ```yaml
   headers:
     Content-Type: application/x-www-form-urlencoded
     Authorization: "Basic {{context.secrets.jenkins_auth}}"
   ```

4. Run the **Solution: Trigger Jenkins Deploy** workflow from the entity page — it reads the Jenkins coordinates from the entity's custom metadata automatically, with no manual inputs required

## Customizing for Production

- Point the workflow at your real entity by replacing `jenkins-demo` with your service tag
- Add `CORTEX_API_KEY` and `CORTEX_BASE_URL` secret-text credentials to your real Jenkins instances
- The Deploy Health scorecard is scoped to `demo-jenkins-deploys` to avoid affecting your existing services. To roll it out broadly, remove the group filter from the scorecard. To opt in individual services, add the `demo-jenkins-deploys` group to them.
