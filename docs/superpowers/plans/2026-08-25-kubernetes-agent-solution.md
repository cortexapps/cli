# Kubernetes Agent Solution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `kubernetes-agent` Cortex CLI solution bundle that deploys the k8s-agent + demo workloads in a GitHub Codespace kind cluster, demonstrating the Cortex k8s integration end-to-end.

**Architecture:** A devcontainer configures a kind cluster on Codespace open; `cortex solutions post-install -s kubernetes-agent` creates k8s secrets, helm-installs the agent from the bundled chart, applies demo workloads, and registers one Cortex entity. The agent auto-registers with Cortex on connect.

**Tech Stack:** Python 3.11+, Typer (CLI), `subprocess` for kubectl/helm, `requests` for GHCR tag fetch + Cortex API, kind (k8s in Docker), helm 3, GitHub Codespaces devcontainer.

**Spec:** `docs/superpowers/specs/2026-08-25-kubernetes-agent-solution-design.md`

## Global Constraints

- Python 3.11+; follow patterns in `cortexapps_cli/solutions/workday/setup.py` exactly
- `SolutionSetup` base class: `cortexapps_cli/solutions/_lib/setup_base.py` — read it before coding `setup.py`
- Solution tag: `kubernetes-agent`; Cortex entity tag: `demo-kubernetes`
- All kubectl/helm calls: `subprocess.run([...], check=True)`
- k8s secret names are fixed: API key secret = `cortex-key` (key field = `api-key`); image pull secret = `cortex-docker-registry-secret`
- Helm chart lives at `cortexapps_cli/solutions/kubernetes-agent/helm-chart/` (bundled, not a remote repo)
- Argo Rollouts CRD URL: `https://raw.githubusercontent.com/argoproj/argo-rollouts/stable/manifests/crds/rollout-crd.yaml`
- GHCR image: `ghcr.io/cortexapps/k8s-agent/k8s-agent`; tag fetched from GitHub API at setup time
- All manifests annotated with `cortex.io/tag: demo-kubernetes`
- Workload names: `demo-deployment`, `demo-statefulset`, `demo-cronjob`, `demo-rollout`

---

## File Map

**Create:**
- `.devcontainer/kubernetes-agent/devcontainer.json` — Codespace config with Docker-in-Docker + tool install
- `.devcontainer/kubernetes-agent/onCreate.sh` — installs kind/kubectl/helm, creates kind cluster
- `cortexapps_cli/solutions/kubernetes-agent/catalog/demo-kubernetes.yaml` — Cortex service entity
- `cortexapps_cli/solutions/kubernetes-agent/manifests/deployment.yaml` — nginx Deployment
- `cortexapps_cli/solutions/kubernetes-agent/manifests/statefulset.yaml` — nginx StatefulSet
- `cortexapps_cli/solutions/kubernetes-agent/manifests/cronjob.yaml` — busybox CronJob
- `cortexapps_cli/solutions/kubernetes-agent/manifests/rollout.yaml` — Argo Rollout (workloadRef → deployment)
- `cortexapps_cli/solutions/kubernetes-agent/helm-chart/` — copied verbatim from `internal/k8s/helm-chart/`
- `cortexapps_cli/solutions/kubernetes-agent/setup.py` — post-install automation script
- `cortexapps_cli/solutions/kubernetes-agent/README.md` — user-facing docs

---

### Task 1: Catalog entity + demo k8s manifests

**Files:**
- Create: `cortexapps_cli/solutions/kubernetes-agent/catalog/demo-kubernetes.yaml`
- Create: `cortexapps_cli/solutions/kubernetes-agent/manifests/deployment.yaml`
- Create: `cortexapps_cli/solutions/kubernetes-agent/manifests/statefulset.yaml`
- Create: `cortexapps_cli/solutions/kubernetes-agent/manifests/cronjob.yaml`
- Create: `cortexapps_cli/solutions/kubernetes-agent/manifests/rollout.yaml`

**Interfaces:**
- Produces: `catalog/demo-kubernetes.yaml` (consumed by Task 3 setup.py entity creation step), manifests dir (consumed by Task 3 manifest apply step)

- [ ] **Step 1: Create the solution directory structure**

```bash
mkdir -p cortexapps_cli/solutions/kubernetes-agent/catalog
mkdir -p cortexapps_cli/solutions/kubernetes-agent/manifests
```

- [ ] **Step 2: Create `catalog/demo-kubernetes.yaml`**

```yaml
openapi: 3.0.0
info:
  title: Demo Kubernetes
  description: Demo entity for the Kubernetes agent integration
  x-cortex-tag: demo-kubernetes
  x-cortex-type: service
```

- [ ] **Step 3: Create `manifests/deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-deployment
  labels:
    app: demo-k8s-label
  annotations:
    cortex.io/tag: demo-kubernetes
spec:
  replicas: 1
  selector:
    matchLabels:
      app: demo-k8s
  template:
    metadata:
      labels:
        app: demo-k8s
    spec:
      containers:
      - name: hello
        image: nginx:alpine
        ports:
        - containerPort: 80
```

- [ ] **Step 4: Create `manifests/statefulset.yaml`**

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: demo-statefulset
  labels:
    app: demo-k8s-label
  annotations:
    cortex.io/tag: demo-kubernetes
spec:
  serviceName: demo-k8s
  replicas: 1
  selector:
    matchLabels:
      app: demo-k8s-ss
  template:
    metadata:
      labels:
        app: demo-k8s-ss
    spec:
      containers:
      - name: hello
        image: nginx:alpine
        ports:
        - containerPort: 80
```

- [ ] **Step 5: Create `manifests/cronjob.yaml`**

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: demo-cronjob
  labels:
    app: demo-k8s-label
  annotations:
    cortex.io/tag: demo-kubernetes
spec:
  schedule: "*/10 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: hello
            image: busybox:latest
            command:
            - /bin/sh
            - -c
            - echo "$(date '+%Y-%m-%d %H:%M:%S') - Hello from demo-kubernetes cronjob" >> /tmp/hello-world.txt
          restartPolicy: OnFailure
```

- [ ] **Step 6: Create `manifests/rollout.yaml`**

The Rollout references `demo-deployment` via `workloadRef` — Cortex resolves containers from the referenced Deployment.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: demo-rollout
  labels:
    app: demo-k8s-label
  annotations:
    cortex.io/tag: demo-kubernetes
spec:
  replicas: 1
  selector:
    matchLabels:
      app: demo-k8s-rollout
  workloadRef:
    apiVersion: apps/v1
    kind: Deployment
    name: demo-deployment
    scaleDown: onsuccess
  strategy:
    canary:
      steps:
        - setWeight: 100
```

- [ ] **Step 7: Validate all YAML files parse correctly**

```bash
python -c "
import yaml, pathlib
for f in pathlib.Path('cortexapps_cli/solutions/kubernetes-agent').rglob('*.yaml'):
    try:
        yaml.safe_load(f.read_text())
        print(f'OK: {f}')
    except yaml.YAMLError as e:
        print(f'FAIL: {f}: {e}')
        exit(1)
"
```

Expected: `OK:` line for each `.yaml` file, no FAIL lines.

- [ ] **Step 8: Commit**

```bash
git add cortexapps_cli/solutions/kubernetes-agent/catalog/ \
        cortexapps_cli/solutions/kubernetes-agent/manifests/
git commit -m "feat: add kubernetes-agent solution catalog entity and demo manifests"
```

---

### Task 2: Bundle helm chart

**Files:**
- Create: `cortexapps_cli/solutions/kubernetes-agent/helm-chart/` (copy of `internal/k8s/helm-chart/`)

**Interfaces:**
- Produces: `helm-chart/` directory (consumed by Task 3 helm install step — path is `Path(__file__).parent / "helm-chart"`)

- [ ] **Step 1: Copy the helm chart from internal**

```bash
cp -r internal/k8s/helm-chart cortexapps_cli/solutions/kubernetes-agent/helm-chart
```

- [ ] **Step 2: Remove the dev-only comment from the deployment template**

The template at `helm-chart/templates/deployment.yaml` has a commented minikube host alias block that is confusing in a public-facing solution. Remove lines 26–31:

```
      ######### remove before deploy - used for local testing ###########
      # hostAliases:
      #  - ip: "192.168.64.1"
      #    hostnames:
      #    - "host.minikube.internal"
      ###################################################################
```

Open `cortexapps_cli/solutions/kubernetes-agent/helm-chart/templates/deployment.yaml` and delete those 6 lines.

- [ ] **Step 3: Add a warning comment to `helm-chart/Chart.yaml`**

Open `cortexapps_cli/solutions/kubernetes-agent/helm-chart/Chart.yaml` and add a comment at the top:

```yaml
# Bundled copy of the Cortex k8s-agent helm chart for demo purposes.
# This copy is not kept up-to-date. Once the chart is published to a
# public helm repo, this bundle will be replaced with a helm repo reference.
apiVersion: v2
name: cortex-k8s-agent
description: A Helm chart for deploying Cortex K8s agent in your cluster
type: application
version: 0.1.0
appVersion: 1.16.0
```

- [ ] **Step 4: Verify helm can render the chart (requires helm installed locally)**

```bash
helm template test-release cortexapps_cli/solutions/kubernetes-agent/helm-chart \
  --set image.tag=test \
  --set app.keySecret=cortex-key \
  --set app.baseUrl=https://api.getcortexapp.com \
  --set app.clusterName=demo \
  > /dev/null && echo "Helm template OK"
```

Expected: `Helm template OK` with no errors. If helm is not installed locally, skip this step — it will be verified in the Codespace.

- [ ] **Step 5: Commit**

```bash
git add cortexapps_cli/solutions/kubernetes-agent/helm-chart/
git commit -m "feat: bundle k8s-agent helm chart in kubernetes-agent solution"
```

---

### Task 3: setup.py

**Files:**
- Create: `cortexapps_cli/solutions/kubernetes-agent/setup.py`

**Interfaces:**
- Consumes: `catalog/demo-kubernetes.yaml` (`Path(__file__).parent / "catalog" / "demo-kubernetes.yaml"`), `manifests/` dir, `helm-chart/` dir
- Consumes: `SolutionSetup` base from `cortexapps_cli/solutions/_lib/setup_base.py` — read this file before writing setup.py to understand all available methods
- Produces: `main(cortex_api_key, cortex_base_url, no_prompt, **kwargs)` entry point (called by `cortex solutions post-install`)

**Before coding:** Read `cortexapps_cli/solutions/_lib/setup_base.py` in full to understand `prompt()`, `confirm()`, `mark_done()`, `already_done()`, `mark_undone()`, and how `steps()` returns `list[tuple[str, callable]]`.

Also read `cortexapps_cli/solutions/workday/setup.py` for the exact class pattern to follow.

- [ ] **Step 1: Create `setup.py` with imports and constants**

```python
"""
Post-install setup script for the kubernetes-agent solution.
Deploys the Cortex k8s-agent to a kind cluster and creates a demo entity.
Run via: cortex solutions post-install -s kubernetes-agent
"""

SETUP_DESCRIPTION = (
    "This solution deploys the Cortex Kubernetes agent to a local kind cluster "
    "and creates a demo entity to demonstrate the k8s integration."
)

import subprocess
import sys
from pathlib import Path

import requests

try:
    from cortexapps_cli.solutions._lib.setup_base import SolutionSetup
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from _lib.setup_base import SolutionSetup

SOLUTION_DIR = Path(__file__).parent
CATALOG_FILE = SOLUTION_DIR / "catalog" / "demo-kubernetes.yaml"
MANIFESTS_DIR = SOLUTION_DIR / "manifests"
HELM_CHART_DIR = SOLUTION_DIR / "helm-chart"

GHCR_IMAGE = "ghcr.io/cortexapps/k8s-agent/k8s-agent"
ARGO_CRD_URL = "https://raw.githubusercontent.com/argoproj/argo-rollouts/stable/manifests/crds/rollout-crd.yaml"
```

- [ ] **Step 2: Create the `KubernetesAgentSetup` class with `__init__` and `collect_prompts`**

```python
class KubernetesAgentSetup(SolutionSetup):
    solution_tag = "kubernetes-agent"

    def __init__(
        self,
        cortex_api_key: str = None,
        cortex_base_url: str = None,
        no_prompt: bool = False,
        **kwargs,
    ):
        super().__init__(no_prompt=no_prompt, **kwargs)
        self._api_key = cortex_api_key or ""
        self._base_url = (cortex_base_url or "https://api.getcortexapp.com").rstrip("/")
        self._ghcr_token = ""
        self._cluster_name = ""

    def _cortex_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/yaml",
        }

    def collect_prompts(self) -> None:
        self._ghcr_token = self.prompt(
            "GHCR_TOKEN",
            description="GitHub PAT with read:packages scope for pulling the k8s-agent image",
            env_var="GHCR_TOKEN",
            secret=True,
        )
        self._cluster_name = self.prompt(
            "cluster_name",
            description="Name for this cluster as it will appear in Cortex",
            default="demo",
        )
```

- [ ] **Step 3: Add `_fetch_image_tag` helper**

```python
    def _fetch_image_tag(self) -> str:
        """Fetch the latest k8s-agent image tag from the GitHub API."""
        r = requests.get(
            "https://api.github.com/orgs/cortexapps/packages/container/k8s-agent%2Fk8s-agent/versions",
            headers={
                "Authorization": f"Bearer {self._ghcr_token}",
                "Accept": "application/vnd.github+json",
            },
        )
        r.raise_for_status()
        versions = r.json()
        if not versions:
            raise RuntimeError("No k8s-agent versions found in GHCR — is GHCR_TOKEN valid?")
        tags = versions[0].get("metadata", {}).get("container", {}).get("tags", [])
        tag = tags[0] if tags else ""
        if not tag:
            raise RuntimeError("Could not determine k8s-agent image tag from GHCR API response")
        print(f"  Using image tag: {tag}")
        return tag
```

- [ ] **Step 4: Add `_create_secrets` step**

```python
    def _create_secrets(self) -> None:
        if self.already_done("create_secrets"):
            return
        print("  Creating cortex-docker-registry-secret...")
        subprocess.run(
            [
                "kubectl", "create", "secret", "docker-registry",
                "cortex-docker-registry-secret",
                "--docker-server=ghcr.io",
                "--docker-username=cortex",
                f"--docker-password={self._ghcr_token}",
                "--dry-run=client", "-o", "yaml",
            ],
            check=True,
            capture_output=True,
        )
        # Pipe output to apply (dry-run=client means we need to apply separately)
        result = subprocess.run(
            [
                "kubectl", "create", "secret", "docker-registry",
                "cortex-docker-registry-secret",
                "--docker-server=ghcr.io",
                "--docker-username=cortex",
                f"--docker-password={self._ghcr_token}",
                "--dry-run=client", "-o", "yaml",
            ],
            check=True,
            capture_output=True,
        )
        subprocess.run(["kubectl", "apply", "-f", "-"], input=result.stdout, check=True)

        print("  Creating cortex-key secret...")
        result = subprocess.run(
            [
                "kubectl", "create", "secret", "generic", "cortex-key",
                f"--from-literal=api-key={self._api_key}",
                "--dry-run=client", "-o", "yaml",
            ],
            check=True,
            capture_output=True,
        )
        subprocess.run(["kubectl", "apply", "-f", "-"], input=result.stdout, check=True)
        self.mark_done("create_secrets")
```

- [ ] **Step 5: Add `_helm_install` step**

```python
    def _helm_install(self) -> None:
        if self.already_done("helm_install"):
            return
        image_tag = self._fetch_image_tag()
        print(f"  Installing k8s-agent via helm (chart: {HELM_CHART_DIR})...")
        subprocess.run(
            [
                "helm", "upgrade", "--install", "cortex-k8s-agent",
                str(HELM_CHART_DIR),
                "--set", f"image.tag={image_tag}",
                "--set", f"app.baseUrl={self._base_url}",
                "--set", f"app.clusterName={self._cluster_name}",
            ],
            check=True,
        )
        # Restart to ensure secrets/configmaps are picked up
        subprocess.run(
            ["kubectl", "rollout", "restart", "deployment",
             "-l", "app.kubernetes.io/name=cortex-k8s-agent"],
            check=True,
        )
        self.mark_done("helm_install")
```

- [ ] **Step 6: Add `_wait_for_readiness` step**

```python
    def _wait_for_readiness(self) -> None:
        if self.already_done("wait_for_readiness"):
            return
        print("  Waiting for k8s-agent pod to be ready (timeout: 120s)...")
        subprocess.run(
            [
                "kubectl", "rollout", "status", "deployment",
                "-l", "app.kubernetes.io/name=cortex-k8s-agent",
                "--timeout=120s",
            ],
            check=True,
        )
        self.mark_done("wait_for_readiness")
```

- [ ] **Step 7: Add `_install_argo_crd` step**

```python
    def _install_argo_crd(self) -> None:
        if self.already_done("install_argo_crd"):
            return
        print(f"  Installing Argo Rollouts CRD...")
        subprocess.run(
            ["kubectl", "apply", "-f", ARGO_CRD_URL],
            check=True,
        )
        self.mark_done("install_argo_crd")
```

- [ ] **Step 8: Add `_apply_manifests` step**

```python
    def _apply_manifests(self) -> None:
        if self.already_done("apply_manifests"):
            return
        print(f"  Applying demo k8s manifests from {MANIFESTS_DIR}...")
        subprocess.run(
            ["kubectl", "apply", "-f", str(MANIFESTS_DIR)],
            check=True,
        )
        self.mark_done("apply_manifests")
```

- [ ] **Step 9: Add `_create_entity` step**

```python
    def _create_entity(self) -> None:
        if self.already_done("create_entity"):
            return
        print(f"  Creating demo-kubernetes Cortex entity...")
        yaml_content = CATALOG_FILE.read_bytes()
        r = requests.post(
            f"{self._base_url}/api/v1/open-api",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/openapi;charset=UTF-8",
            },
            data=yaml_content,
        )
        if not r.ok:
            raise RuntimeError(
                f"Failed to create Cortex entity: {r.status_code} {r.text}"
            )
        self.mark_done("create_entity")
```

- [ ] **Step 10: Add `steps`, `post_steps`, and `main`**

```python
    def steps(self) -> list:
        return [
            ("Create k8s secrets", self._create_secrets),
            ("Install k8s-agent via helm", self._helm_install),
            ("Wait for agent readiness", self._wait_for_readiness),
            ("Install Argo Rollouts CRD", self._install_argo_crd),
            ("Apply demo k8s manifests", self._apply_manifests),
            ("Create demo Cortex entity", self._create_entity),
        ]

    def post_steps(self) -> None:
        print("\n✓ Kubernetes agent deployed and demo workloads running.\n")
        print("The agent syncs every 5 minutes. After the first sync, visit:")
        print(f"  {self._base_url.replace('api.', 'app.')}/catalog/demo-kubernetes/k8s")
        print("\nYou should see: demo-deployment, demo-statefulset, demo-cronjob, demo-rollout")
        print("\nNote: GHCR_TOKEN requirement goes away once the k8s-agent image is made public.")


def main(cortex_api_key=None, cortex_base_url=None, no_prompt=False, **kwargs):
    KubernetesAgentSetup(
        cortex_api_key=cortex_api_key,
        cortex_base_url=cortex_base_url,
        no_prompt=no_prompt,
    ).run()


if __name__ == "__main__":
    main()
```

- [ ] **Step 11: Verify the script imports cleanly (no syntax errors)**

```bash
python -c "import cortexapps_cli.solutions.kubernetes_agent.setup as s; print('OK')"
```

If that path doesn't work (no `__init__.py`), try:

```bash
cd cortexapps_cli/solutions/kubernetes-agent && python -c "import setup; print('OK')"
```

Expected: `OK`

- [ ] **Step 12: Commit**

```bash
git add cortexapps_cli/solutions/kubernetes-agent/setup.py
git commit -m "feat: add kubernetes-agent solution post-install setup script"
```

---

### Task 4: Devcontainer

**Files:**
- Create: `.devcontainer/kubernetes-agent/devcontainer.json`
- Create: `.devcontainer/kubernetes-agent/onCreate.sh`

**Interfaces:**
- Produces: a working Codespace environment with kind cluster running, `CORTEX_API_KEY` and `GHCR_TOKEN` available as env vars from Codespace secrets

- [ ] **Step 1: Create `devcontainer.json`**

```json
{
  "name": "Cortex Kubernetes Agent Demo",
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu-24.04",
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {},
    "ghcr.io/devcontainers/features/kubectl-helm-minikube:1": {
      "version": "latest",
      "helm": "latest",
      "minikube": "none"
    }
  },
  "onCreateCommand": "bash .devcontainer/kubernetes-agent/onCreate.sh",
  "remoteEnv": {
    "CORTEX_API_KEY": "${localEnv:CORTEX_API_KEY}",
    "GHCR_TOKEN": "${localEnv:GHCR_TOKEN}"
  },
  "postCreateMessage": "Run: cortex solutions install -s kubernetes-agent && cortex solutions post-install -s kubernetes-agent"
}
```

Note: `kubectl-helm-minikube` feature installs kubectl + helm without minikube (set to `"none"`). kind is installed separately in `onCreate.sh`.

- [ ] **Step 2: Create `onCreate.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "==> Installing kind..."
curl -Lo /usr/local/bin/kind \
  https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x /usr/local/bin/kind

echo "==> Creating kind cluster 'cortex-demo'..."
kind create cluster --name cortex-demo --wait 60s

echo "==> Verifying cluster..."
kubectl cluster-info --context kind-cortex-demo

echo "==> Installing cortexapps-cli..."
pip install cortexapps-cli --quiet

echo "==> Done. Run: cortex solutions post-install -s kubernetes-agent"
```

- [ ] **Step 3: Verify `devcontainer.json` is valid JSON**

```bash
python -c "import json; json.load(open('.devcontainer/kubernetes-agent/devcontainer.json')); print('OK')"
```

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add .devcontainer/kubernetes-agent/
git commit -m "feat: add kubernetes-agent Codespace devcontainer"
```

---

### Task 5: README

**Files:**
- Create: `cortexapps_cli/solutions/kubernetes-agent/README.md`

- [ ] **Step 1: Create `README.md`**

```markdown
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
- A GitHub PAT with `read:packages` scope (`GHCR_TOKEN`) — request from Cortex support

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
```

- [ ] **Step 2: Commit**

```bash
git add cortexapps_cli/solutions/kubernetes-agent/README.md
git commit -m "docs: add kubernetes-agent solution README"
```

---

## Self-Review

**Spec coverage check:**
- ✓ Devcontainer with Docker-in-Docker, kind install, onCreate → Task 4
- ✓ `cortex solutions install` + `cortex solutions post-install` flow → Tasks 1–3 (install picks up catalog/; post-install runs setup.py)
- ✓ Create k8s image pull secret (`cortex-docker-registry-secret`) → Task 3 Step 4
- ✓ Create API key secret (`cortex-key`, key `api-key`) → Task 3 Step 4
- ✓ Fetch image tag from GHCR API → Task 3 Step 3
- ✓ Helm install from bundled chart → Task 3 Step 5
- ✓ Wait for agent readiness → Task 3 Step 6
- ✓ Install Argo Rollouts CRD → Task 3 Step 7
- ✓ Apply 4 demo manifests (Deployment, StatefulSet, CronJob, Rollout) → Tasks 1 + 3 Step 8
- ✓ Rollout `workloadRef` points to `demo-deployment` → Task 1 Step 6
- ✓ Create `demo-kubernetes` Cortex entity → Task 3 Step 9
- ✓ Warning about GHCR_TOKEN requirement → Task 3 Step 10 (post_steps), Task 5 README
- ✓ Dev comment removed from helm chart deployment template → Task 2 Step 2
- ✓ Helm chart bundle warning comment → Task 2 Step 3

**No placeholders found.**

**Type consistency:** All step method names referenced in `steps()` (Task 3 Step 10) match the method definitions in Steps 4–9. `CATALOG_FILE`, `MANIFESTS_DIR`, `HELM_CHART_DIR` constants defined once in Step 1 and used consistently throughout.
