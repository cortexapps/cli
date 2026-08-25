# Kubernetes Agent Solution Design

**Date:** 2026-08-25
**Status:** Approved
**Linear:** [CX-14](https://linear.app/cortexio/issue/CX-14/cli-solution-kubernetes)

## Overview

A Cortex CLI solution bundle that demonstrates the Kubernetes agent integration end-to-end. Users run the solution inside a GitHub Codespace with a pre-configured kind cluster. One command installs the k8s-agent (via public helm chart), deploys sample workloads (Deployment, StatefulSet, CronJob, Argo Rollout), and configures a demo entity in Cortex — making it easy to show how the integration works without any local setup.

**Audience:** Internal testers initially; broadens when the k8s-agent image is made public.

---

## Architecture

### Two-Phase Setup

**Phase 1 — Devcontainer (one-time Codespace initialization)**

`.devcontainer/kubernetes-agent/devcontainer.json` configures the Codespace environment:

- Base image: `mcr.microsoft.com/devcontainers/base:ubuntu` with Docker-in-Docker feature
- `onCreate` script installs: `kind`, `kubectl`, `helm`
- `onCreate` script creates the kind cluster: `kind create cluster --name cortex-demo`

Users pre-set two Codespace secrets before opening the Codespace:
- `CORTEX_API_KEY` — their Cortex API key
- `GHCR_TOKEN` — GitHub PAT with `read:packages` scope (requested from Cortex support until image is public)

Both secrets are injected as environment variables automatically when the Codespace starts.

**Phase 2 — Solution post-install (user-initiated)**

```bash
cortex solutions install -s kubernetes-agent
cortex solutions post-install -s kubernetes-agent
```

The post-install script (`setup.py`) runs the following steps in order, with idempotency via `already_done()` / `mark_done()` state:

1. **Prompt for inputs** — `CORTEX_API_KEY`, `GHCR_TOKEN`, `CORTEX_BASE_URL` (default: `https://api.getcortexapp.com`), cluster name (default: `demo`)
2. **Create k8s image pull secret** — `kubectl create secret docker-registry cortex-ghcr-secret --docker-server=ghcr.io --docker-username=<user> --docker-password=<GHCR_TOKEN>`
3. **Helm install k8s-agent** — from the public helm chart repo; passes `CORTEX_API_KEY`, `CORTEX_BASE_URL`, cluster name, and pull secret name as values
4. **Wait for agent readiness** — polls `kubectl rollout status deployment/k8s-agent` with timeout
5. **Install Argo Rollouts CRD** — `kubectl apply -f <argo-rollouts-crds-url>`
6. **Apply demo k8s manifests** — `kubectl apply -f manifests/` (Deployment, StatefulSet, CronJob, Rollout — all annotated `cortex.io/tag: demo-kubernetes`)
7. **Create demo Cortex entity** — `cortex catalog create -f catalog/demo-kubernetes.yaml`

Agent auto-registers with Cortex on connect using the API key — no explicit Cortex-side integration configuration step required.

---

## Solution Bundle Structure

```
cortexapps_cli/solutions/kubernetes-agent/
├── README.md
├── setup.py
├── catalog/
│   └── demo-kubernetes.yaml          # demo service entity, tag: demo-kubernetes
└── manifests/                        # k8s demo workloads (sourced from internal/k8s/manifests)
    ├── deployment.yaml               # nginx Deployment, annotated cortex.io/tag: demo-kubernetes
    ├── statefulset.yaml              # StatefulSet, annotated cortex.io/tag: demo-kubernetes
    ├── cronjob.yaml                  # CronJob, annotated cortex.io/tag: demo-kubernetes
    └── rollout.yaml                  # Argo Rollout (workloadRef → deployment), annotated demo-kubernetes
```

```
.devcontainer/kubernetes-agent/
├── devcontainer.json
└── onCreate.sh                       # kind cluster creation + tool install script
```

### Demo Entity (`catalog/demo-kubernetes.yaml`)

```yaml
openapi: 3.0.0
info:
  title: Demo Kubernetes
  description: Demo entity for the Kubernetes agent integration
  x-cortex-tag: demo-kubernetes
  x-cortex-type: service
```

### Demo Manifests

All four manifests are adapted from `internal/k8s/manifests/` with the cortex tag updated from `k8s-test-annotation` to `demo-kubernetes`. The Rollout uses `workloadRef` pointing to the Deployment (same pattern as `k8s-test-rollout.yaml`).

---

## Helm Chart

The k8s-agent helm chart is public. The solution uses `helm repo add` + `helm install` — the chart URL needs to be confirmed and hardcoded before implementation begins.

Key helm values passed by the setup script:
- `cortexApiKey` — from `CORTEX_API_KEY`
- `cortexBaseUrl` — from `CORTEX_BASE_URL`
- `clusterName` — from user prompt (default: `demo`)
- `image.pullSecrets[0].name` — `cortex-ghcr-secret`

---

## `setup.py` Design

Follows the `SolutionSetup` base class pattern (same as workday):

```python
class KubernetesAgentSetup(SolutionSetup):
    solution_tag = "kubernetes-agent"

    def collect_prompts(self):
        # Prompt for CORTEX_API_KEY, GHCR_TOKEN, CORTEX_BASE_URL, cluster name
        # Reads from env vars first (Codespace secrets auto-inject them)

    def steps(self):
        return [
            ("Create image pull secret", self._create_pull_secret),
            ("Install k8s-agent via helm", self._helm_install),
            ("Wait for agent readiness", self._wait_for_readiness),
            ("Install Argo Rollouts CRD", self._install_argo_crds),
            ("Apply demo k8s manifests", self._apply_manifests),
            ("Create demo Cortex entity", self._create_entity),
        ]

    def post_steps(self):
        # Print success message + link to Cortex entity k8s tab
```

State persistence via `~/.cortex/solutions/kubernetes-agent.json` ensures re-runs skip completed steps.

---

## Devcontainer

`.devcontainer/kubernetes-agent/devcontainer.json`:
- Uses Docker-in-Docker feature so kind can run containers inside the Codespace container
- `onCreate` installs kind, kubectl, helm via apt/curl/brew and creates the `cortex-demo` kind cluster
- Codespace secrets (`CORTEX_API_KEY`, `GHCR_TOKEN`) are automatically available as env vars in the terminal

---

## Image Credential Note

The k8s-agent container image (`ghcr.io/cortexapps/k8s-agent/k8s-agent`) is currently private on GHCR. Users need a `GHCR_TOKEN` (GitHub PAT, `read:packages` scope) obtained from Cortex support. This requirement goes away once the image is made public — the pull secret creation step will be removed at that point.

---

## Out of Scope (v1)

- Scorecard
- Making the GHCR image public (tracked separately)
- Playwright UI verification (internal tooling only)
- Local machine support (Codespace only for v1)

---

## Open Questions

1. **Helm chart URL** — needs to be confirmed before implementation. Is it hosted at a `cortexapps` GitHub Pages repo?
2. **Argo Rollouts CRD URL** — standard upstream URL (`https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml`) or a pinned version?
3. **`GHCR_TOKEN` username** — does the pull secret need a real GitHub username or can it be a placeholder (some GHCR PATs work with any username)?
