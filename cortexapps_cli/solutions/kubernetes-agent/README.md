---
name: Kubernetes Agent
description: Deploy the Cortex Kubernetes agent to a kind cluster in a GitHub Codespace, or to any existing Kubernetes cluster, to demonstrate live workload discovery and k8s integration.
---

# Kubernetes Agent Solution

Demonstrates the [Cortex Kubernetes agent](https://docs.cortex.io/docs/reference/integrations/kubernetes) integration. Supports two deployment paths:

- **GitHub Codespace** — creates a Codespace with a local [kind](https://kind.sigs.k8s.io) cluster automatically (no cluster setup required)
- **Existing cluster** — deploys to any Kubernetes cluster already configured in your `kubectl` context

## What this installs

- **Cortex k8s-agent** — connects your cluster to Cortex and syncs workload metadata
- **Demo workloads** — Deployment, StatefulSet, CronJob, and Argo Rollout, all tagged `demo-kubernetes`
- **demo-kubernetes** — a Cortex service entity that the workloads annotate to

After setup, visit your entity's K8s tab to see live workload data synced from the cluster.

## Data Model

```
  GitHub Codespace
  ┌──────────────────────────────────────────────────────────┐
  │  kind cluster (cortex-demo)                              │
  │  ┌────────────────────────────────────────────────────┐  │
  │  │                                                    │  │
  │  │  ┌─────────────────┐   ┌──────────────────────┐    │  │
  │  │  │  Kubernetes API │◀──│  cortex-k8s-agent    │    │  │
  │  │  │  Server         │   │  (polls every 5 min) │    │  │
  │  │  └─────────────────┘   └──────────┬───────────┘    │  │
  │  │                                   │ HTTPS push     │  │
  │  │  ┌──────────────────────────────┐ │                │  │
  │  │  │  demo workloads              │ │                │  │
  │  │  │  Deployment · StatefulSet    │ │                │  │
  │  │  │  CronJob · Argo Rollout      │ │                │  │
  │  │  └──────────────────────────────┘ │                │  │
  │  └────────────────────────────────────────────────────┘  │
  └──────────────────────────────────┬───────────────────────┘
                                     ▼
                           ┌─────────────────┐
                           │  Cortex         │
                           │  Platform       │
                           └─────────────────┘
```

The agent runs inside the cluster as a Deployment. Every 5 minutes it queries the Kubernetes API for workload resources and pushes the metadata to Cortex over HTTPS. Cortex surfaces the data on each entity's K8s tab.

## Prerequisites

- A Cortex API key (`CORTEX_API_KEY`) — get from Cortex Settings → API Keys
- A GitHub PAT provided by Cortex Customer Engineering (`GHCR_TOKEN`) — required to pull the k8s-agent image; see [Kubernetes prerequisites](https://docs.cortex.io/ingesting-data-into-cortex/integrations/kubernetes#prerequisites)

**For the GitHub Codespace path only:**
- The [gh CLI](https://cli.github.com) installed and authenticated (`gh auth login`)

**For the existing cluster path only:**
- `kubectl`, `helm` installed and configured to reach your cluster

## Quick start

```bash
cortex solutions install -s kubernetes-agent
cortex solutions post-install -s kubernetes-agent
```

The setup script will ask which path you want:

```
Create a new GitHub Codespace with a kind cluster? (yes = spin up Codespace, no = use an existing configured cluster) [yes]:
```

### GitHub Codespace path

The script will:
1. Create a Codespace from the `cortexapps/cli` repository using the `kubernetes-agent` devcontainer
2. Wait for the Codespace to start and the kind cluster to initialize (~15-20 min on first run)
3. Deploy the k8s-agent and demo workloads inside the Codespace via `gh codespace ssh`

After setup, the Codespace URL and `gh codespace ssh` command are printed.

### Existing cluster path

Requires `kubectl` pointed at a running cluster. The script deploys the k8s-agent and demo workloads into whatever namespace your current context targets.

## What you should see

After the agent's first sync (~5 min), visit:
`https://app.getcortexapp.com/admin/resources?tag=demo-kubernetes`

- `demo-deployment` (Deployment)
- `demo-statefulset` (StatefulSet)
- `demo-cronjob` (CronJob)
- `demo-rollout` (Argo Rollout — containers resolved from `demo-deployment`)

## Troubleshooting

**No K8s details showing on the entity page after the first sync**

If you have configured [K8s metadata label customization](https://docs.cortex.io/ingesting-data-into-cortex/integrations/kubernetes#auto-mapping-customization) in your Cortex settings (Settings → Kubernetes → Metadata labels), Cortex uses *only* those labels for resource mapping and ignores the `cortex.io/tag` annotation used by the demo manifests. Either:

- Remove the metadata label customization to use the default annotation-based mapping, or
- Add a matching label (e.g., `app: demo-kubernetes`) to the demo manifests

## Re-running setup

The setup script is idempotent — re-run `cortex solutions post-install -s kubernetes-agent` to retry any failed step. Completed steps are skipped.

For the Codespace path, the Codespace name is saved locally so re-runs reconnect to the same Codespace rather than creating a new one.

## After Installing

Once you have verified the agent working against the demo cluster, roll it out to your real clusters:

1. **Install the Cortex Kubernetes agent Helm chart into each cluster** for which you want data associated with your Cortex entities. Give each cluster a distinct `clusterName` — this is how Cortex identifies which cluster a workload belongs to:

   ```bash
   helm upgrade --install cortex-k8s-agent \
     oci://ghcr.io/cortexapps/k8s-agent/helm/cortex-k8s-agent \
     --set app.apiKey=<your-cortex-api-key> \
     --set app.clusterName=<name-as-it-appears-in-cortex> \
     --set app.baseUrl=https://api.getcortexapp.com
   ```

2. **Ensure your Kubernetes workloads have the appropriate annotation or label** so Cortex can map them to your catalog entities:

   - **Annotation** (default): add `cortex.io/tag: <entity-tag>` to each workload's metadata
   - **Label** (if you have configured K8s metadata label customization in Cortex Settings): add the configured label key with the entity tag as the value, e.g. `app: <entity-tag>`

3. **Wait for the first sync** (~5 min) then visit each entity's K8s tab in Cortex to confirm workload data is flowing.

See the [Cortex Kubernetes integration docs](https://docs.cortex.io/ingesting-data-into-cortex/integrations/kubernetes) for full configuration options including namespace filtering, custom resource types, and RBAC setup.

## Temporary limitation

The k8s-agent image is currently private on GHCR, requiring `GHCR_TOKEN`. This requirement will be removed once the image is made public.
