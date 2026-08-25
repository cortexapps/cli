---
name: Kubernetes Agent
description: Deploy the Cortex Kubernetes agent in a GitHub Codespace with a local kind cluster to demonstrate live workload discovery and k8s integration.
---

# Kubernetes Agent Solution

Demonstrates the [Cortex Kubernetes agent](https://docs.cortex.io/docs/reference/integrations/kubernetes) integration using a GitHub Codespace with a local kind cluster.

## What this installs

- **Cortex k8s-agent** — connects your cluster to Cortex and syncs workload metadata
- **Demo workloads** — Deployment, StatefulSet, CronJob, and Argo Rollout, all tagged `demo-kubernetes`
- **demo-kubernetes** — a Cortex service entity that the workloads annotate to

After setup, visit your entity's K8s tab to see live workload data synced from the cluster.

## Prerequisites

- A [GitHub Codespace](https://github.com/features/codespaces) opened from this repository
- A Cortex API key (`CORTEX_API_KEY`) — get from Cortex Settings → API Keys
- A GitHub PAT with `read:packages` scope (`GHCR_TOKEN`) — see [Kubernetes prerequisites](https://docs.cortex.io/ingesting-data-into-cortex/integrations/kubernetes#prerequisites)

Set both as [Codespace secrets](https://docs.github.com/en/codespaces/managing-your-codespaces/managing-secrets-for-your-codespaces) before opening the Codespace.

## Quick start

1. Open a Codespace from this repository (select the `kubernetes-agent` devcontainer configuration)
2. Wait for `onCreate` to finish (installs tools + creates kind cluster, ~2 min)
3. Run the solution:

```bash
cortex solutions install -s kubernetes-agent
cortex solutions post-install -s kubernetes-agent
```

4. Wait ~5 minutes for the agent's first sync, then visit:
   `https://app.getcortexapp.com/catalog/demo-kubernetes/k8s`

## What you should see

- `demo-deployment` (Deployment)
- `demo-statefulset` (StatefulSet)
- `demo-cronjob` (CronJob)
- `demo-rollout` (Argo Rollout — containers resolved from `demo-deployment`)

## Re-running setup

The setup script is idempotent — re-run `cortex solutions post-install -s kubernetes-agent` to retry any failed step. Completed steps are skipped.

## Temporary limitation

The k8s-agent image is currently private on GHCR, requiring `GHCR_TOKEN`. This requirement will be removed once the image is made public.
