# SKE + Cortex Integration Test Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up SKE on minikube with a trivial ConfigMap Promise and validate the Cortex integration creates Entity Types, Workflows, and provisions resources end-to-end.

**Architecture:** Minikube cluster running SKE Operator + Kratix, ArgoCD for GitOps, and the SKE Cortex Controller. A ConfigMap Promise labeled `kratix.io/cortex: "true"` triggers automatic creation of Cortex Entity Types and Workflows. The test verifies the full flow from Cortex Workflow trigger to ConfigMap appearing on the cluster.

**Tech Stack:** Kubernetes (minikube), Helm 3, ArgoCD, Kratix CLI, Python (pipeline), Just (task runner), gh CLI

---

### Task 1: Create directory structure and environment config

**Files:**
- Create: `internal/ske/` (directory)
- Modify: `internal/.env.example`

- [ ] **Step 1: Create the ske directory**

```bash
mkdir -p internal/ske
```

- [ ] **Step 2: Add SKE variables to .env.example**

Append this block to the end of `internal/.env.example`:

```bash
# ---------------------------------------------------------------------------
# SKE (Syntasso Kratix Enterprise)
# ---------------------------------------------------------------------------

# Syntasso license token. This ghp_-prefixed GitHub PAT is used for both
# the SKE license and pulling images from ghcr.io/syntasso.
SKE_LICENSE_TOKEN=

# SKE version to install (e.g., v0.99.0). Check Syntasso docs for latest.
SKE_VERSION=v0.99.0
```

- [ ] **Step 3: Add the same variables to your local .env**

```bash
# Add to internal/.env (not committed):
SKE_LICENSE_TOKEN=<your-token>
SKE_VERSION=v0.99.0
```

- [ ] **Step 4: Commit**

```bash
git add internal/ske/.gitkeep internal/.env.example
git commit -m "feat: add SKE directory structure and env config"
```

Note: Create an empty `.gitkeep` in `internal/ske/` so the directory is tracked.

---

### Task 2: Scaffold and customize the ConfigMap Promise

**Files:**
- Create: `internal/ske/promise.yaml`
- Create: `internal/ske/example-resource.yaml`
- Create: `internal/ske/workflows/resource/configure/message-configure/ske-test-message-pipeline/scripts/pipeline.py`
- Create: `internal/ske/workflows/resource/configure/message-configure/ske-test-message-pipeline/Dockerfile`

- [ ] **Step 1: Scaffold the Promise with Kratix CLI**

```bash
cd internal/ske
~/go/bin/kratix init promise message --group demo.cortex.io --kind Message
~/go/bin/kratix update api --property message:string
~/go/bin/kratix add container resource/configure/message-configure \
  --image ske-test/message-pipeline:v0.1.0 --language python
```

This generates `promise.yaml`, `example-resource.yaml`, and the pipeline scaffold.

- [ ] **Step 2: Add the Cortex label to promise.yaml**

Edit `internal/ske/promise.yaml` — add `kratix.io/cortex: "true"` to the labels block:

```yaml
metadata:
  labels:
    kratix.io/promise-version: v0.0.1
    kratix.io/cortex: "true"
  name: message
```

- [ ] **Step 3: Write the pipeline script**

Replace the contents of `internal/ske/workflows/resource/configure/message-configure/ske-test-message-pipeline/scripts/pipeline.py` with:

```python
import kratix_sdk as ks
import yaml


def main():
    sdk = ks.KratixSDK()
    resource = sdk.read_resource_input()
    name = resource.get_name()
    message = resource.get_value("spec.message")

    configmap = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {
            "name": name,
            "namespace": "default",
        },
        "data": {
            "message": message,
        },
    }

    data = yaml.safe_dump(configmap).encode("utf-8")
    sdk.write_output("configmap.yaml", data)

    status = ks.Status()
    status.set("message", message)
    sdk.write_status(status)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Update example-resource.yaml**

Replace `internal/ske/example-resource.yaml` with:

```yaml
apiVersion: demo.cortex.io/v1alpha1
kind: Message
metadata:
  name: example-message
  namespace: default
spec:
  message: "hello from ske"
```

- [ ] **Step 5: Remove the scaffolded README.md**

```bash
rm internal/ske/README.md
```

The Kratix CLI generates a README we don't need.

- [ ] **Step 6: Commit**

```bash
git add internal/ske/
git commit -m "feat: add ConfigMap Promise for SKE Cortex integration test"
```

---

### Task 3: Create Helm values and ArgoCD Application manifest

**Files:**
- Create: `internal/ske/values.yaml`
- Create: `internal/ske/argocd-app.yaml`

- [ ] **Step 1: Create the SKE Helm values file**

Create `internal/ske/values.yaml`:

```yaml
# SKE Operator Helm values for local minikube testing.
# Environment variables are substituted at install time via --set overrides.
#
# Usage (from Justfile):
#   helm install ske-operator syntasso/ske-operator \
#     --namespace kratix-platform-system \
#     --create-namespace --wait \
#     --values ske/values.yaml \
#     --set skeLicense=${SKE_LICENSE_TOKEN} \
#     --set cortexIntegration.config.token=${CORTEX_API_KEY} \
#     --set cortexIntegration.config.url=${CORTEX_BASE_URL}

skeDeployment:
  version: v0.99.0

cortexIntegration:
  enabled: true
  version: "latest"
  config:
    branch: main
    integrationAlias: github
    path: kratix-resource-requests
    provider: github
    repositoryName: jeff-test-org/ske-test-resources
```

- [ ] **Step 2: Create the ArgoCD Application manifest**

Create `internal/ske/argocd-app.yaml`:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: kratix-cortex-resources
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/jeff-test-org/ske-test-resources
    targetRevision: HEAD
    path: .
    directory:
      recurse: true
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    automated:
      selfHeal: true
      prune: true
```

- [ ] **Step 3: Commit**

```bash
git add internal/ske/values.yaml internal/ske/argocd-app.yaml
git commit -m "feat: add SKE Helm values and ArgoCD Application manifest"
```

---

### Task 4: Write the `ske-setup` Justfile recipe

**Files:**
- Modify: `internal/Justfile`

- [ ] **Step 1: Add the SKE section to the Justfile**

Append the following block to `internal/Justfile` (before any trailing blank lines):

```just
# ---------------------------------------------------------------------------
# SKE (Syntasso Kratix Enterprise)
# ---------------------------------------------------------------------------

# Start minikube, install ArgoCD + SKE, deploy ConfigMap Promise
ske-setup:
    #!/usr/bin/env bash
    set -euo pipefail

    # 1. Start minikube if not running
    if minikube status | grep -q "Running"; then
        echo "minikube already running"
    else
        echo "Starting minikube..."
        minikube start --memory=8192 --cpus=4
    fi

    # 2. Create GitHub repo for GitOps (idempotent)
    echo "Ensuring GitHub repo jeff-test-org/ske-test-resources exists..."
    gh repo create jeff-test-org/ske-test-resources --public --clone=false 2>/dev/null || \
        echo "  Repo already exists."

    # 3. Install ArgoCD
    echo "Installing ArgoCD..."
    kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
    kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
    echo "Waiting for ArgoCD to be ready..."
    kubectl wait --for=condition=available deployment/argocd-server \
        -n argocd --timeout=300s

    # 4. Apply ArgoCD Application to watch the GitOps repo
    echo "Configuring ArgoCD Application..."
    kubectl apply -f ske/argocd-app.yaml

    # 5. Create GHCR image pull secret for Syntasso images
    echo "Creating image pull secret for Syntasso GHCR..."
    kubectl create namespace kratix-platform-system --dry-run=client -o yaml | kubectl apply -f -
    kubectl create secret docker-registry syntasso-registry \
        --namespace=kratix-platform-system \
        --docker-server=ghcr.io \
        --docker-username=syntasso-pkg \
        --docker-password="${SKE_LICENSE_TOKEN}" \
        --dry-run=client -o yaml | kubectl apply -f -

    # 6. Install SKE Operator via Helm
    echo "Installing SKE Operator..."
    helm repo add syntasso https://syntasso.github.io/helm-charts 2>/dev/null || true
    helm repo update syntasso
    helm upgrade --install ske-operator syntasso/ske-operator \
        --namespace kratix-platform-system \
        --create-namespace --wait \
        --values ske/values.yaml \
        --set skeLicense="${SKE_LICENSE_TOKEN}" \
        --set skeDeployment.version="${SKE_VERSION}" \
        --set cortexIntegration.config.token="${CORTEX_API_KEY}" \
        --set cortexIntegration.config.url="${CORTEX_BASE_URL}"

    # 7. Wait for Kratix pods to be ready
    echo "Waiting for Kratix platform pods..."
    kubectl wait --for=condition=available deployment --all \
        -n kratix-platform-system --timeout=300s

    # 8. Build and load pipeline image into minikube
    echo "Building pipeline image..."
    docker build -t ske-test/message-pipeline:v0.1.0 \
        ske/workflows/resource/configure/message-configure/ske-test-message-pipeline
    echo "Loading pipeline image into minikube..."
    minikube image load ske-test/message-pipeline:v0.1.0

    # 9. Install the ConfigMap Promise
    echo "Installing ConfigMap Promise..."
    kubectl apply -f ske/promise.yaml

    # 10. Wait for Promise to become Available
    echo "Waiting for Promise to become Available..."
    for i in $(seq 1 60); do
        STATUS=$(kubectl get promise message -o jsonpath='{.status.conditions[?(@.type=="Available")].status}' 2>/dev/null || echo "")
        if [ "$STATUS" = "True" ]; then
            echo "Promise is Available!"
            break
        fi
        if [ "$i" -eq 60 ]; then
            echo "Warning: Promise did not become Available within 120s"
            kubectl get promise message -o yaml
            exit 1
        fi
        sleep 2
    done

    echo ""
    echo "SKE setup complete."
    echo "  - Kratix:  kubectl get pods -n kratix-platform-system"
    echo "  - Promise: kubectl get promise message"
    echo "  - ArgoCD:  kubectl port-forward svc/argocd-server -n argocd 8080:443"
    echo ""
    echo "Run 'just ske-test' to verify the Cortex integration."
```

- [ ] **Step 2: Verify the Justfile syntax**

```bash
cd internal && just --list | grep ske
```

Expected output includes `ske-setup`.

- [ ] **Step 3: Commit**

```bash
git add internal/Justfile
git commit -m "feat: add ske-setup Justfile recipe"
```

---

### Task 5: Write the `ske-test` Justfile recipe

**Files:**
- Modify: `internal/Justfile`

- [ ] **Step 1: Add the ske-test recipe**

Append after the `ske-setup` recipe in `internal/Justfile`:

```just
# Verify Cortex integration: Entity Type, Workflows, and ConfigMap provisioning
ske-test:
    #!/usr/bin/env bash
    set -euo pipefail

    echo "=== Step 1: Check for Message Entity Type in Cortex ==="
    MAX_ATTEMPTS=30
    SLEEP_SECONDS=10
    for i in $(seq 1 $MAX_ATTEMPTS); do
        # List entity types and look for "Message"
        RESPONSE=$(curl -sf \
            -H "Authorization: Bearer ${CORTEX_API_KEY}" \
            "${CORTEX_BASE_URL}/api/v1/catalog/types" 2>&1) || true
        if echo "$RESPONSE" | grep -q '"message"'; then
            echo "  Entity Type 'message' found in Cortex!"
            break
        fi
        if [ "$i" -eq "$MAX_ATTEMPTS" ]; then
            echo "FAILED: Entity Type 'message' not found in Cortex after $((MAX_ATTEMPTS * SLEEP_SECONDS))s"
            echo "Last response: $RESPONSE"
            exit 1
        fi
        echo "  Attempt $i/$MAX_ATTEMPTS: waiting ${SLEEP_SECONDS}s for SKE controller to create Entity Type..."
        sleep $SLEEP_SECONDS
    done

    echo ""
    echo "=== Step 2: Check for auto-generated Workflows in Cortex ==="
    WORKFLOWS=$(curl -sf \
        -H "Authorization: Bearer ${CORTEX_API_KEY}" \
        "${CORTEX_BASE_URL}/api/v1/workflows" 2>&1) || true
    # The SKE controller generates workflows with predictable names
    echo "  Available workflows:"
    echo "$WORKFLOWS" | python3 -m json.tool 2>/dev/null | grep -i "message" || echo "  (checking...)"

    echo ""
    echo "=== Step 3: Trigger Create Workflow via Cortex API ==="
    echo "  Sending resource request with message='hello from ske'..."

    # Find the create workflow tag for the Message promise
    CREATE_WF_TAG=$(echo "$WORKFLOWS" | python3 -c "
import json, sys
data = json.load(sys.stdin)
workflows = data.get('workflows', data) if isinstance(data, dict) else data
for wf in (workflows if isinstance(workflows, list) else [workflows]):
    tag = wf.get('tag', '')
    name = wf.get('name', '').lower()
    if 'message' in name.lower() and 'create' in name.lower():
        print(tag)
        break
" 2>/dev/null || echo "")

    if [ -z "$CREATE_WF_TAG" ]; then
        echo "FAILED: Could not find a Create workflow for Message"
        echo "Workflows response:"
        echo "$WORKFLOWS" | python3 -m json.tool 2>/dev/null || echo "$WORKFLOWS"
        exit 1
    fi
    echo "  Found create workflow: $CREATE_WF_TAG"

    # Trigger the workflow
    RUN_RESPONSE=$(curl -sf \
        -H "Authorization: Bearer ${CORTEX_API_KEY}" \
        -H "Content-Type: application/json" \
        -X POST "${CORTEX_BASE_URL}/api/v1/workflows/${CREATE_WF_TAG}/runs" \
        -d '{"parameters": {"message": "hello from ske"}, "scope": {"type": "GLOBAL"}}')
    RUN_ID=$(echo "$RUN_RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('id',''))" 2>/dev/null || echo "")
    echo "  Workflow run ID: $RUN_ID"

    echo ""
    echo "=== Step 4: Wait for ConfigMap to appear on cluster ==="
    MAX_ATTEMPTS=60
    SLEEP_SECONDS=5
    for i in $(seq 1 $MAX_ATTEMPTS); do
        CM_DATA=$(kubectl get configmap -n default -o json 2>/dev/null | \
            python3 -c "
import json, sys
data = json.load(sys.stdin)
for item in data.get('items', []):
    d = item.get('data', {})
    if d.get('message') == 'hello from ske':
        print(item['metadata']['name'])
        break
" 2>/dev/null || echo "")
        if [ -n "$CM_DATA" ]; then
            echo "  ConfigMap '$CM_DATA' found with message='hello from ske'!"
            echo ""
            echo "SUCCESS: Full SKE → Cortex → GitOps → Cluster flow verified!"
            exit 0
        fi
        if [ "$i" -eq "$MAX_ATTEMPTS" ]; then
            echo "FAILED: ConfigMap with message='hello from ske' not found after $((MAX_ATTEMPTS * SLEEP_SECONDS))s"
            echo "ConfigMaps in default namespace:"
            kubectl get configmap -n default
            exit 1
        fi
        echo "  Attempt $i/$MAX_ATTEMPTS: waiting ${SLEEP_SECONDS}s for ConfigMap..."
        sleep $SLEEP_SECONDS
    done
```

- [ ] **Step 2: Verify the recipe appears**

```bash
cd internal && just --list | grep ske-test
```

- [ ] **Step 3: Commit**

```bash
git add internal/Justfile
git commit -m "feat: add ske-test Justfile recipe"
```

---

### Task 6: Write the `ske-stop` Justfile recipe

**Files:**
- Modify: `internal/Justfile`

- [ ] **Step 1: Add the ske-stop recipe**

Append after the `ske-test` recipe in `internal/Justfile`:

```just
# Tear down SKE, ArgoCD, and stop minikube
ske-stop:
    #!/usr/bin/env bash
    set -euo pipefail

    echo "Deleting ConfigMap Promise..."
    kubectl delete promise message 2>/dev/null || true

    echo "Uninstalling SKE Operator..."
    helm uninstall ske-operator -n kratix-platform-system 2>/dev/null || true

    echo "Removing ArgoCD..."
    kubectl delete -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml 2>/dev/null || true
    kubectl delete namespace argocd 2>/dev/null || true

    echo "Stopping minikube..."
    minikube stop

    echo "Done."
```

- [ ] **Step 2: Commit**

```bash
git add internal/Justfile
git commit -m "feat: add ske-stop Justfile recipe"
```

---

### Task 7: Run `ske-setup` and iterate

This is the hands-on validation task. No code to write — just run and debug.

- [ ] **Step 1: Ensure .env has the required variables**

Verify `internal/.env` contains:
- `CORTEX_API_KEY` (existing)
- `CORTEX_BASE_URL` (existing)
- `GITHUB_TOKEN` (existing)
- `GH_USER` (existing)
- `SKE_LICENSE_TOKEN` (new)
- `SKE_VERSION=v0.99.0` (new)

- [ ] **Step 2: Run ske-setup**

```bash
cd internal && just ske-setup
```

Watch for errors at each step. Common issues:
- GHCR auth failure → check `SKE_LICENSE_TOKEN` is valid
- Helm chart not found → `helm repo update syntasso`
- Pod image pull errors → check the syntasso-registry secret was created in the right namespace
- Promise stays "Unavailable" → `kubectl describe promise message` for details

- [ ] **Step 3: Verify pods are running**

```bash
kubectl get pods -n kratix-platform-system
```

Expected: SKE operator and Kratix controller pods all Running/Ready.

- [ ] **Step 4: Verify Promise is Available**

```bash
kubectl get promise message
```

Expected: STATUS = Available.

- [ ] **Step 5: Check that the Cortex controller created resources**

```bash
# Check Entity Types
curl -sf -H "Authorization: Bearer ${CORTEX_API_KEY}" \
    "${CORTEX_BASE_URL}/api/v1/catalog/types" | python3 -m json.tool | grep -i message

# Check Workflows
curl -sf -H "Authorization: Bearer ${CORTEX_API_KEY}" \
    "${CORTEX_BASE_URL}/api/v1/workflows" | python3 -m json.tool | grep -i message
```

---

### Task 8: Run `ske-test` and validate end-to-end

- [ ] **Step 1: Run the test**

```bash
cd internal && just ske-test
```

- [ ] **Step 2: If the test passes, celebrate**

The full flow is working: SKE Promise → Cortex Entity Type + Workflows → Workflow trigger → GitOps → ConfigMap on cluster.

- [ ] **Step 3: If the test fails, debug**

Common failure points:
- Entity Type not created → Check Cortex controller logs: `kubectl logs -n kratix-platform-system -l app=cortex-controller`
- Workflow trigger fails → Check the workflow payload format matches what SKE generated
- ConfigMap never appears → Check ArgoCD sync: `kubectl get applications -n argocd`, check the GitHub repo for committed files
- GitOps sync delay → Increase polling timeout or manually trigger ArgoCD sync

- [ ] **Step 4: Run ske-stop to clean up**

```bash
cd internal && just ske-stop
```

- [ ] **Step 5: Final commit if any adjustments were made**

```bash
git add -A
git commit -m "fix: adjust SKE integration test based on validation"
```
