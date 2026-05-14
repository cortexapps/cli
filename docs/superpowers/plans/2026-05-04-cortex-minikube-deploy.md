# Cortex Minikube Deploy + Shared Cluster Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Cortex self-hosted deploy to the internal Justfile, share a single minikube cluster across all modules, and add guided env var prompting for all recipes.

**Architecture:** A shared `_minikube-start` recipe manages cluster lifecycle via named profile. A shared `_ensure-env` bash helper prompts for missing env vars with help text. New `cortex-setup/stop/status/pf/db/open` recipes deploy Cortex via Helm. Existing k8s-agent and SKE recipes are refactored to use the shared primitives.

**Tech Stack:** Just (task runner), Bash, Helm, minikube, kubectl

**Spec:** `docs/superpowers/specs/2026-05-04-cortex-minikube-deploy-design.md`

---

### File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `internal/Justfile` | Modify | All recipes — shared helpers, new cortex recipes, refactored k8s-agent/SKE, env prompting |
| `internal/cortex/values.yaml` | Create | Helm values for cortex/cortex chart (port-forward mode, PostgreSQL subchart) |
| `internal/.env.example` | Modify | Add minikube profile, GH_PAT, CORTEX_LICENSE_FILE vars |
| `internal/CLAUDE.md` | Modify | Document new recipes, shared profile, env prompting |

---

### Task 1: Create `internal/cortex/values.yaml`

**Files:**
- Create: `internal/cortex/values.yaml`

- [ ] **Step 1: Create the cortex directory**

Run: `mkdir -p /Users/jeffschnitter/git/cli/internal/cortex`

- [ ] **Step 2: Write values.yaml**

Create `internal/cortex/values.yaml` with:

```yaml
# Cortex on minikube — port-forward only, no ingress
# Deploy with: helm upgrade --install cortex cortex/cortex --values cortex/values.yaml

app:
  hostnames:
    frontend: "localhost:3000"
    backend: "localhost:8080"
    protocol: http

  ingress:
    create: false
    enabled: false

  backend:
    replicaCount: 1
    jvmConfiguration:
      javaOpts: -Xms512m -Xmx4096m -Dpolyglot.engine.Mode=interpreted
    containerConfiguration:
      resources:
        requests:
          memory: 4Gi
          cpu: 1
        limits:
          memory: 4Gi
          cpu: 2

  worker:
    replicaCount: 1
    jvmConfiguration:
      javaOpts: -Xms512m -Xmx1536m
    containerConfiguration:
      resources:
        requests:
          memory: 3Gi
          cpu: 1
        limits:
          memory: 5Gi
          cpu: 2

  frontend:
    replicaCount: 1

  ai:
    enabled: false
  api:
    enabled: false
  graph:
    enabled: false
  workflowsRunner:
    enabled: false

postgresql:
  enabled: true
  auth:
    postgresPassword: "cortex"
    username: "cortex"
    password: "cortex"
    database: "cortex"
  primary:
    persistence:
      enabled: true
      size: 4Gi
    resources:
      requests:
        memory: 256Mi
        cpu: 250m
      limits:
        memory: 1Gi
        cpu: 1000m

redis:
  enabled: false
```

- [ ] **Step 3: Commit**

```bash
git add internal/cortex/values.yaml
git commit -m "feat: add Cortex Helm values for minikube deploy"
```

---

### Task 2: Update `.env.example` with new vars

**Files:**
- Modify: `internal/.env.example`

- [ ] **Step 1: Add minikube and cortex deploy sections**

Insert after the SKE section (end of file) in `internal/.env.example`:

```
# ---------------------------------------------------------------------------
# Minikube shared cluster
# ---------------------------------------------------------------------------

# Minikube profile name. Defaults to cortex-minikube if not set.
# MINIKUBE_PROFILE=cortex-minikube

# ---------------------------------------------------------------------------
# Cortex self-hosted deploy (minikube)
# ---------------------------------------------------------------------------

# GitHub PAT for pulling Cortex images from ghcr.io. Needs read:packages scope.
# Create at GitHub > Settings > Developer settings > Personal access tokens.
GH_PAT=

# Absolute path to your Cortex license JWT file.
# Get from 1Password vault 'Cortex Licenses' or ask in #engineering Slack channel.
CORTEX_LICENSE_FILE=
```

- [ ] **Step 2: Commit**

```bash
git add internal/.env.example
git commit -m "feat: add minikube profile and cortex deploy vars to .env.example"
```

---

### Task 3: Rewrite Justfile — shared helpers and header

This is the largest task. The entire Justfile is being rewritten to add the shared helpers at the top and thread them through all recipes. Do this in one commit since the helpers and the recipes that use them are tightly coupled.

**Files:**
- Modify: `internal/Justfile`

- [ ] **Step 1: Replace the Justfile header and add shared helpers**

Replace everything from the top of the file through the `help:` recipe (lines 1-9) with:

```just
set dotenv-load
set export

MINIKUBE_PROFILE := env("MINIKUBE_PROFILE", "cortex-minikube")

cortex_cli := 'poetry run cortex'
pytest := 'PYTHONPATH=..:../tests poetry run pytest -rA'
pw_pytest := 'poetry run pytest -rA --headed --browser chromium'

help:
   @just -l

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

# Start minikube if not already running (shared across all k8s recipes)
_minikube-start:
    #!/usr/bin/env bash
    set -euo pipefail
    if minikube status --profile {{MINIKUBE_PROFILE}} 2>/dev/null | grep -q "Running"; then
        echo "minikube ({{MINIKUBE_PROFILE}}) already running"
    else
        echo "Starting minikube ({{MINIKUBE_PROFILE}})..."
        minikube start --memory=10240 --cpus=4 --driver=docker --profile={{MINIKUBE_PROFILE}}
    fi
    kubectl config use-context {{MINIKUBE_PROFILE}}

# Check for required env vars, prompt for missing ones, append to .env.
# Each argument is "NAME|Label|Help text".
_ensure-env +vars:
    #!/usr/bin/env bash
    set -euo pipefail

    # Create .env from .env.example if it doesn't exist
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            echo "Created .env from .env.example"
        else
            touch .env
        fi
    fi

    # Source current .env values
    set -a
    source .env
    set +a

    # Parse var declarations and find missing ones
    MISSING_NAMES=()
    MISSING_LABELS=()
    MISSING_HELPS=()
    for decl in {{vars}}; do
        NAME=$(echo "$decl" | cut -d'|' -f1)
        LABEL=$(echo "$decl" | cut -d'|' -f2)
        HELP=$(echo "$decl" | cut -d'|' -f3)
        VAL="${!NAME:-}"
        if [ -z "$VAL" ]; then
            MISSING_NAMES+=("$NAME")
            MISSING_LABELS+=("$LABEL")
            MISSING_HELPS+=("$HELP")
        fi
    done

    if [ ${#MISSING_NAMES[@]} -eq 0 ]; then
        exit 0
    fi

    echo ""
    echo "Missing ${#MISSING_NAMES[@]} required variable(s): ${MISSING_NAMES[*]}"
    echo ""

    for i in "${!MISSING_NAMES[@]}"; do
        NAME="${MISSING_NAMES[$i]}"
        LABEL="${MISSING_LABELS[$i]}"
        HELP="${MISSING_HELPS[$i]}"

        echo "$NAME ($LABEL)"
        echo "  $HELP"
        while true; do
            printf ": "
            read -r VALUE
            if [ -n "$VALUE" ]; then
                echo "$NAME=$VALUE" >> .env
                export "$NAME=$VALUE"
                echo ""
                break
            fi
            echo "  Value cannot be empty. Try again."
        done
    done

    echo "All variables set."
    echo ""

# Stop the shared minikube cluster
minikube-stop:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Stopping minikube ({{MINIKUBE_PROFILE}})..."
    minikube stop --profile {{MINIKUBE_PROFILE}}
    echo "Done."
```

- [ ] **Step 2: Add `_ensure-env` calls to functional test recipes**

Replace the functional test section (lines 11-21 in original) with:

```just
# ---------------------------------------------------------------------------
# Functional tests
# ---------------------------------------------------------------------------

# Import functional test data (workflows)
test-functional-import: (_ensure-env "CORTEX_API_KEY|Cortex API key|Get from Cortex Settings > API Keys. Needs 'Run workflows' and 'View workflow runs' permissions." "CORTEX_BASE_URL|Cortex API base URL|Defaults to https://api.getcortexapp.com. Override for self-hosted instances.")
   {{pytest}} -m setup tests/test_functional_import.py --cov=cortexapps_cli --cov-report=

# Run functional tests, ie: just test-functional tests/test_gh_branches.py
test-functional *args: (_ensure-env "CORTEX_API_KEY|Cortex API key|Get from Cortex Settings > API Keys. Needs 'Run workflows' and 'View workflow runs' permissions." "CORTEX_BASE_URL|Cortex API base URL|Defaults to https://api.getcortexapp.com. Override for self-hosted instances.")
   {{pytest}} -v -s -n auto --dist loadgroup -m functional --html=report-functional.html --self-contained-html {{args}}

# Clean up orphaned functional test resources from interrupted runs
_test-functional-clean:
   {{pytest}} -v -s -m cleanup tests/test_gh_sweep.py
```

- [ ] **Step 3: Rewrite k8s-agent recipes**

Replace the entire K8s agent section (lines 23-132 in original) with:

```just
# ---------------------------------------------------------------------------
# K8s agent
# ---------------------------------------------------------------------------

# Start minikube, deploy k8s-agent, deploy test objects + Cortex entity
k8s-agent-setup: (_ensure-env "GH_USER|GitHub username|Your GitHub username for GHCR authentication." "GITHUB_TOKEN|GitHub PAT|Create at GitHub > Settings > Developer settings > Personal access tokens. Needs read:packages scope." "CORTEX_API_KEY|Cortex API key|Get from Cortex Settings > API Keys." "CORTEX_BASE_URL|Cortex API base URL|Defaults to https://api.getcortexapp.com. Override for self-hosted instances.") _minikube-start
    #!/usr/bin/env bash
    set -euo pipefail

    # 1. Create docker registry secret for GHCR
    kubectl create secret docker-registry cortex-docker-registry-secret \
        --docker-server=ghcr.io \
        --docker-username="${GH_USER}" \
        --docker-password="${GITHUB_TOKEN}" \
        --dry-run=client -o yaml | kubectl apply -f -

    # 2. Create cortex-key secret
    kubectl create secret generic cortex-key \
        --from-literal=api-key="${CORTEX_API_KEY}" \
        --dry-run=client -o yaml | kubectl apply -f -

    # 3. Fetch latest k8s-agent image tag from GHCR
    echo "Fetching latest k8s-agent image tag..."
    IMAGE_TAG=$(gh api \
        -H "Accept: application/vnd.github+json" \
        /orgs/cortexapps/packages/container/k8s-agent%2Fk8s-agent/versions \
        --jq '.[0].metadata.container.tags[0]')
    echo "Using image tag: ${IMAGE_TAG}"

    # 4. Helm install/upgrade k8s-agent
    helm upgrade --install cortex-k8s-agent k8s/helm-chart \
        --set image.tag="${IMAGE_TAG}" \
        --set app.baseUrl="${CORTEX_BASE_URL}"

    # 5. Wait for agent pod readiness
    echo "Waiting for k8s-agent pod to be ready..."
    for i in $(seq 1 30); do
        if kubectl get pod -l app.kubernetes.io/name=cortex-k8s-agent 2>/dev/null | grep -q .; then
            break
        fi
        sleep 2
    done
    kubectl wait --for=condition=ready pod \
        -l app.kubernetes.io/name=cortex-k8s-agent \
        --timeout=120s

    # 6. Create Cortex entity
    echo "Creating Cortex entity..."
    {{cortex_cli}} catalog create -f k8s/cortex-entity.yaml || true

    # 7. Apply test k8s manifests
    echo "Applying test manifests..."
    kubectl apply -f k8s/manifests/

    echo "Setup complete. Run 'just k8s-agent-test' to verify."

# Verify test objects show up in Cortex via CLI
k8s-agent-test: (_ensure-env "CORTEX_API_KEY|Cortex API key|Get from Cortex Settings > API Keys." "CORTEX_BASE_URL|Cortex API base URL|Defaults to https://api.getcortexapp.com.")
    #!/usr/bin/env bash
    set -euo pipefail

    echo "Waiting for k8s-agent to push data to Cortex..."
    MAX_ATTEMPTS=30
    SLEEP_SECONDS=10

    for i in $(seq 1 $MAX_ATTEMPTS); do
        RESPONSE=$({{cortex_cli}} rest get /api/v1/catalog/k8s-test-annotation/k8s 2>&1) || true

        # Check for all three expected objects
        HAS_DEPLOYMENT=$(echo "$RESPONSE" | grep -c '"k8s-deployment"' || true)
        HAS_STATEFULSET=$(echo "$RESPONSE" | grep -c '"k8s-statefulset"' || true)
        HAS_CRONJOB=$(echo "$RESPONSE" | grep -c '"k8s-cronjob"' || true)

        if [ "$HAS_DEPLOYMENT" -gt 0 ] && [ "$HAS_STATEFULSET" -gt 0 ] && [ "$HAS_CRONJOB" -gt 0 ]; then
            echo "All k8s objects found in Cortex!"
            echo "  - k8s-deployment"
            echo "  - k8s-statefulset"
            echo "  - k8s-cronjob"
            exit 0
        fi

        echo "Attempt $i/$MAX_ATTEMPTS: waiting ${SLEEP_SECONDS}s for agent to sync..."
        sleep $SLEEP_SECONDS
    done

    echo "FAILED: Not all k8s objects appeared in Cortex after $((MAX_ATTEMPTS * SLEEP_SECONDS))s"
    echo "Last response:"
    echo "$RESPONSE"
    exit 1

# Tear down k8s-agent (keeps minikube running)
k8s-agent-stop:
    #!/usr/bin/env bash
    set -euo pipefail

    echo "Uninstalling k8s-agent..."
    helm uninstall cortex-k8s-agent || true

    echo "Done."
```

- [ ] **Step 4: Add `_ensure-env` to Playwright recipes**

Replace the Playwright section (lines 134-148 in original) with:

```just
# ---------------------------------------------------------------------------
# Playwright UI tests
# ---------------------------------------------------------------------------

# Run all Playwright UI tests
test-ui *args: (_ensure-env "CORTEX_APP_URL|Cortex web app URL|Defaults to https://app.getcortexapp.com." "CORTEX_TENANT_CODE|Cortex tenant code|Found in your Cortex URL: app.getcortexapp.com/<tenant-code>." "GOOGLE_EMAIL|Google account email|The Google account used for SSO login to Cortex." "GOOGLE_PASSWORD|Google account password|Password for the Google SSO account." "GOOGLE_TOTP_URI|Google TOTP URI|otpauth:// URI for generating MFA codes. Get when setting up 2FA — choose 'Can't scan it?' to see the secret.")
   {{pw_pytest}} -v ui/tests/ {{args}}

# Run Workday integration tests (Playwright + API polling)
test-workday *args: (_ensure-env "CORTEX_APP_URL|Cortex web app URL|Defaults to https://app.getcortexapp.com." "CORTEX_TENANT_CODE|Cortex tenant code|Found in your Cortex URL: app.getcortexapp.com/<tenant-code>." "GOOGLE_EMAIL|Google account email|The Google account used for SSO login to Cortex." "GOOGLE_PASSWORD|Google account password|Password for the Google SSO account." "GOOGLE_TOTP_URI|Google TOTP URI|otpauth:// URI for generating MFA codes. Get when setting up 2FA — choose 'Can't scan it?' to see the secret." "WORKDAY_USERNAME|Workday service account username|Workday service account for the ownership report API." "WORKDAY_PASSWORD|Workday service account password|Password for the Workday service account." "WORKDAY_OWNERSHIP_REPORT_URL|Workday report URL|Workday custom report URL that returns ownership data.")
   {{pw_pytest}} -v ui/tests/test_workday.py {{args}}

# Launch Playwright codegen to record a new test
test-ui-create name url="https://app.getcortexapp.com/admin/home":
   poetry run playwright codegen --target python-pytest -o ui/tests/{{name}}.py --load-storage=ui/state.json {{url}}
```

- [ ] **Step 5: Add `_ensure-env` to axon recipes**

Replace the axon-setup recipe body (lines 155-187 in original). Remove the manual `if [ -z "${CORTEX_API_KEY:-}" ]` check and add `_ensure-env` as a dependency:

```just
# ---------------------------------------------------------------------------
# Axon relay
# ---------------------------------------------------------------------------

# Start axon relay containers for configured integrations
axon-setup: (_ensure-env "CORTEX_API_KEY|Cortex API key|Get from Cortex Settings > API Keys.")
    #!/usr/bin/env bash
    set -euo pipefail

    services=()

    [ -n "${GITHUB_TOKEN:-}" ] && services+=(github)
    [ -n "${GITLAB_TOKEN:-}" ] && services+=(gitlab)
    [ -n "${JIRA_TOKEN:-}" ] && services+=(jira)
    [ -n "${BITBUCKET_USERNAME:-}" ] && [ -n "${BITBUCKET_PASSWORD:-}" ] && services+=(bitbucket)
    [ -n "${SONAR_TOKEN:-}" ] && services+=(sonarqube)
    [ -n "${PROMETHEUS_API:-}" ] && services+=(prometheus)

    if [ ${#services[@]} -eq 0 ]; then
        echo "No integrations configured. Set variables in .env for the integrations you want:"
        echo "  - GitHub:     GITHUB_TOKEN"
        echo "  - GitLab:     GITLAB_TOKEN"
        echo "  - Jira:       JIRA_TOKEN"
        echo "  - Bitbucket:  BITBUCKET_USERNAME + BITBUCKET_PASSWORD"
        echo "  - SonarQube:  SONAR_TOKEN"
        echo "  - Prometheus: PROMETHEUS_API"
        exit 0
    fi

    echo "Starting axon relay for: ${services[*]}"
    docker compose -f axon/compose.yaml up -d "${services[@]}"
    echo "Done. Running containers:"
    docker compose -f axon/compose.yaml ps
```

Keep `axon-status` and `axon-stop` unchanged (no env vars needed).

Replace the axon-test recipe header (line 202) to add `_ensure-env` and remove the manual check:

```just
# Set up Jenkins + relay, create pipeline job, push workflow to Cortex
axon-test: (_ensure-env "CORTEX_API_KEY|Cortex API key|Get from Cortex Settings > API Keys.")
    #!/usr/bin/env bash
    set -euo pipefail

    # 1. Build and start Jenkins
```

Remove the `if [ -z "${CORTEX_API_KEY:-}" ]` block (lines 207-209 in original) from inside the axon-test recipe body. Keep everything else in axon-test the same.

Replace the axon-echo-setup recipe header (line 306) similarly:

```just
# Set up echo server + relay, push workflow to Cortex
axon-echo-setup: (_ensure-env "CORTEX_API_KEY|Cortex API key|Get from Cortex Settings > API Keys.")
    #!/usr/bin/env bash
    set -euo pipefail

    echo "Starting echo server + relay..."
```

Remove the `if [ -z "${CORTEX_API_KEY:-}" ]` block (lines 310-313) from axon-echo-setup body.

Replace the axon-echo-test recipe header (line 346):

```just
# Trigger the echo workflow and wait for completion
axon-echo-test: (_ensure-env "CORTEX_API_KEY|Cortex API key|Get from Cortex Settings > API Keys." "CORTEX_BASE_URL|Cortex API base URL|Defaults to https://api.getcortexapp.com.")
    #!/usr/bin/env bash
    set -euo pipefail

    echo "Triggering echo workflow..."
```

Keep `axon-test-logs`, `axon-test-stop`, `axon-echo-logs`, `axon-echo-stop` unchanged.

- [ ] **Step 6: Prometheus recipes stay unchanged**

`prometheus-setup` and `prometheus-stop` need no env vars. Leave them as-is.

- [ ] **Step 7: Rewrite SKE recipes**

Replace ske-setup recipe header and minikube section (lines 412-422 in original). Add `_ensure-env` dependency and `_minikube-start` dependency, remove inline minikube start:

```just
# ---------------------------------------------------------------------------
# SKE (Syntasso Kratix Enterprise)
# ---------------------------------------------------------------------------

# Start minikube, install ArgoCD + SKE, deploy ConfigMap Promise
ske-setup: (_ensure-env "SKE_LICENSE_TOKEN|Syntasso license token|ghp_-prefixed GitHub PAT from Syntasso. Used for both the SKE license and pulling images from ghcr.io/syntasso." "CORTEX_API_KEY|Cortex API key|Get from Cortex Settings > API Keys." "CORTEX_BASE_URL|Cortex API base URL|Defaults to https://api.getcortexapp.com." "GH_USER|GitHub username|Your GitHub username for git-credentials secret." "GITHUB_TOKEN|GitHub PAT|Create at GitHub > Settings > Developer settings > Personal access tokens. Needs repo scope for GitOps repo access.") _minikube-start
    #!/usr/bin/env bash
    set -euo pipefail

    # 1. Create GitHub repo for GitOps (idempotent)
    echo "Ensuring GitHub repo jeff-test-org/ske-test-resources exists..."
```

Everything from step 2 onward in ske-setup stays the same, EXCEPT replace the one `minikube image load` line (line 483) with:

```bash
    minikube image load ske-test/message-pipeline:v0.1.0 --profile {{MINIKUBE_PROFILE}}
```

Replace ske-stop to remove `minikube stop`:

```just
# Tear down SKE, ArgoCD, and cert-manager (keeps minikube running)
ske-stop:
    #!/usr/bin/env bash
    set -euo pipefail

    echo "Cleaning up test resource from GitHub repo..."
    SHA=$(gh api repos/jeff-test-org/ske-test-resources/contents/kratix-resource-requests/ske-test-msg.yaml --jq '.sha' 2>/dev/null || echo "")
    if [ -n "$SHA" ]; then
        gh api repos/jeff-test-org/ske-test-resources/contents/kratix-resource-requests/ske-test-msg.yaml \
            --method DELETE \
            -f message="test: clean up ske-test-msg resource" \
            -f sha="$SHA" 2>/dev/null || true
    fi

    echo "Deleting ConfigMap Promise..."
    kubectl delete promise message 2>/dev/null || true

    echo "Deleting Destinations and GitStateStore..."
    kubectl delete destination --all 2>/dev/null || true
    kubectl delete gitstatestore default 2>/dev/null || true

    echo "Uninstalling SKE Operator..."
    helm uninstall ske-operator -n kratix-platform-system 2>/dev/null || true

    echo "Removing cert-manager..."
    kubectl delete -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml 2>/dev/null || true

    echo "Removing ArgoCD..."
    kubectl delete -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml 2>/dev/null || true
    kubectl delete namespace argocd 2>/dev/null || true

    echo "Done."
```

Add `_ensure-env` to `ske-test` recipe header:

```just
# Verify Cortex integration: Entity Type, Workflows, and ConfigMap provisioning
ske-test: (_ensure-env "CORTEX_API_KEY|Cortex API key|Get from Cortex Settings > API Keys." "CORTEX_BASE_URL|Cortex API base URL|Defaults to https://api.getcortexapp.com.")
    #!/usr/bin/env bash
    set -euo pipefail
```

The rest of the `ske-test` body stays unchanged.

- [ ] **Step 8: Add Cortex deploy recipes**

Add after the Prometheus section, before the SKE section:

```just
# ---------------------------------------------------------------------------
# Cortex self-hosted deploy (minikube)
# ---------------------------------------------------------------------------

# Deploy Cortex on minikube: database, backend, worker, frontend + port forwarding
cortex-setup: (_ensure-env "GH_USER|GitHub username|Your GitHub username for ghcr.io authentication." "GH_PAT|GitHub PAT for ghcr.io|Create at GitHub > Settings > Developer settings > Personal access tokens. Needs read:packages scope for pulling Cortex container images." "CORTEX_LICENSE_FILE|Path to license.jwt|Get from 1Password vault 'Cortex Licenses' or ask in #engineering Slack. Save the file anywhere and provide the absolute path.") _minikube-start
    #!/usr/bin/env bash
    set -euo pipefail

    # Validate license file exists
    if [ ! -f "${CORTEX_LICENSE_FILE}" ]; then
        echo "Error: License file not found at ${CORTEX_LICENSE_FILE}"
        exit 1
    fi

    # 1. Create GHCR pull secret
    echo "Creating GHCR pull secret..."
    kubectl create secret docker-registry cortex-docker-registry-secret \
        --docker-server=ghcr.io \
        --docker-username="${GH_USER}" \
        --docker-password="${GH_PAT}" \
        --dry-run=client -o yaml | kubectl apply -f -

    # 2. Create cortex-secret with DB creds + license
    echo "Creating Cortex secret..."
    kubectl create secret generic cortex-secret \
        --from-literal=DB_HOST=cortex-postgresql \
        --from-literal=DB_PORT=5432 \
        --from-literal=DB_USERNAME=cortex \
        --from-literal=DB_NAME=cortex \
        --from-literal=DB_PASSWORD=cortex \
        --from-literal=ENTITLEMENTS_JWT="$(cat "${CORTEX_LICENSE_FILE}")" \
        --dry-run=client -o yaml | kubectl apply -f -

    # 3. Install/upgrade Cortex via Helm
    echo "Adding Cortex Helm repo..."
    helm repo add cortex https://helm-charts.cortex.io 2>/dev/null || true
    helm repo update cortex

    CHART_VERSION=$(helm search repo cortex/cortex -o json | jq -r '.[0].version' 2>/dev/null || echo "unknown")
    echo "Deploying Cortex (chart version: ${CHART_VERSION})..."
    helm upgrade --install cortex cortex/cortex \
        --values cortex/values.yaml \
        --timeout 15m \
        --wait

    # 4. Wait for pods
    echo "Waiting for Cortex pods to be ready..."
    kubectl wait --for=condition=ready pod -l app=cortex-frontend --timeout=300s
    kubectl wait --for=condition=ready pod -l app=cortex-backend --timeout=300s

    # 5. Set up port forwarding
    pkill -f "kubectl.*port-forward.*cortex-frontend-service" || true
    pkill -f "kubectl.*port-forward.*cortex-backend-service" || true
    sleep 1

    kubectl port-forward svc/cortex-frontend-service 3000:80 >/dev/null 2>&1 &
    echo $! > /tmp/cortex-frontend-pf.pid
    kubectl port-forward svc/cortex-backend-service 8080:80 >/dev/null 2>&1 &
    echo $! > /tmp/cortex-backend-pf.pid
    sleep 2

    echo ""
    echo "Cortex is running!"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend:  http://localhost:8080"
    echo ""
    echo "Use 'just cortex-pf' to resume port forwarding after sleep/reboot."
    echo "Use 'just cortex-stop' to tear down."

# Tear down Cortex deployment (keeps minikube running)
cortex-stop:
    #!/usr/bin/env bash
    set -euo pipefail

    # Stop port forwards
    pkill -f "kubectl.*port-forward.*cortex-frontend-service" || true
    pkill -f "kubectl.*port-forward.*cortex-backend-service" || true
    rm -f /tmp/cortex-frontend-pf.pid /tmp/cortex-backend-pf.pid

    echo "Uninstalling Cortex..."
    helm uninstall cortex || true

    echo "Done."

# Show Cortex pod and port-forward status
cortex-status:
    #!/usr/bin/env bash
    echo "Cortex Status"
    echo "============="
    echo ""
    echo "Pods:"
    kubectl get pods -l app.kubernetes.io/name=cortex-deployment 2>/dev/null || echo "  No Cortex pods found"
    echo ""
    echo "Services:"
    kubectl get svc | grep cortex 2>/dev/null || echo "  No Cortex services found"
    echo ""
    if pgrep -f "kubectl.*port-forward.*cortex-frontend-service" > /dev/null 2>&1; then
        echo "Frontend port forward: RUNNING (http://localhost:3000)"
    else
        echo "Frontend port forward: NOT RUNNING"
    fi
    if pgrep -f "kubectl.*port-forward.*cortex-backend-service" > /dev/null 2>&1; then
        echo "Backend port forward: RUNNING (http://localhost:8080)"
    else
        echo "Backend port forward: NOT RUNNING"
    fi

# Resume port forwarding (after sleep/reboot)
cortex-pf:
    #!/usr/bin/env bash
    set -euo pipefail

    if ! minikube status --profile {{MINIKUBE_PROFILE}} 2>/dev/null | grep -q "Running"; then
        echo "Error: minikube ({{MINIKUBE_PROFILE}}) is not running. Run 'just cortex-setup' first."
        exit 1
    fi

    pkill -f "kubectl.*port-forward.*cortex-frontend-service" || true
    pkill -f "kubectl.*port-forward.*cortex-backend-service" || true
    sleep 1

    kubectl port-forward svc/cortex-frontend-service 3000:80 >/dev/null 2>&1 &
    echo $! > /tmp/cortex-frontend-pf.pid
    kubectl port-forward svc/cortex-backend-service 8080:80 >/dev/null 2>&1 &
    echo $! > /tmp/cortex-backend-pf.pid
    sleep 2

    echo "Port forwarding established:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend:  http://localhost:8080"

# Connect to Cortex PostgreSQL database
cortex-db:
    #!/usr/bin/env bash
    set -euo pipefail
    POD=$(kubectl get pods -l app.kubernetes.io/name=postgresql -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    if [ -z "$POD" ]; then
        echo "Error: No PostgreSQL pod found. Run 'just cortex-setup' first."
        exit 1
    fi
    kubectl exec -it "$POD" -- psql -U cortex -d cortex

# Open Cortex frontend in browser
cortex-open:
    @open http://localhost:3000
```

- [ ] **Step 9: Verify the full Justfile**

Run: `cd /Users/jeffschnitter/git/cli/internal && just help`

Expected: All recipes listed without syntax errors. Output should show the new cortex-* recipes, minikube-stop, and all existing recipes.

- [ ] **Step 10: Commit the Justfile**

```bash
git add internal/Justfile
git commit -m "feat: shared minikube cluster, env prompting, cortex deploy recipes"
```

---

### Task 4: Update `internal/CLAUDE.md`

**Files:**
- Modify: `internal/CLAUDE.md`

- [ ] **Step 1: Add shared minikube and cortex deploy documentation**

Add the following sections to `internal/CLAUDE.md`. Insert a "Shared minikube cluster" section before the existing "Quick reference" section, and add a "Cortex self-hosted deploy" section after the SKE section.

Add to the quick reference block:

```bash
# Shared minikube cluster
just minikube-stop            # stop the shared cluster (all modules)

# Cortex self-hosted deploy
just cortex-setup             # deploy Cortex on minikube
just cortex-stop              # tear down Cortex (keeps cluster)
just cortex-status            # show pod/port-forward status
just cortex-pf                # resume port forwarding after sleep
just cortex-db                # psql into local postgres
just cortex-open              # open http://localhost:3000
```

Add a new section:

```markdown
## Shared minikube cluster

All k8s-based recipes (cortex, k8s-agent, SKE) share a single minikube cluster with profile `cortex-minikube` (configurable via `MINIKUBE_PROFILE` in `.env`). Each module has independent setup/stop recipes that manage only their own Helm releases. Use `just minikube-stop` to stop the cluster entirely.

## Cortex self-hosted deploy

Deploys Cortex (backend, worker, frontend, PostgreSQL) on the shared minikube cluster via the `cortex/cortex` Helm chart.

### Required environment variables

| Variable | Description |
|----------|-------------|
| `GH_USER` | GitHub username for ghcr.io authentication |
| `GH_PAT` | GitHub PAT with `read:packages` scope |
| `CORTEX_LICENSE_FILE` | Absolute path to your `license.jwt` file |

All vars are prompted automatically if missing from `.env`.

### Using k8s-agent with local Cortex

To point the k8s-agent at your local Cortex instead of cloud:

```bash
# In .env, set:
CORTEX_BASE_URL=http://cortex-backend-service:80
```

The agent communicates via K8s service DNS — no port-forward needed.
```

- [ ] **Step 2: Update existing sections to note shared profile**

In the k8s-agent quick reference, update the comment on `just k8s-agent-stop` from "tear down + stop minikube" to "tear down k8s-agent (keeps cluster)".

In the SKE quick reference, update `just ske-stop` from "tear down everything + stop minikube" to "tear down SKE/ArgoCD/cert-manager (keeps cluster)".

- [ ] **Step 3: Add env prompting documentation**

Add a section after the Environment section:

```markdown
## Env var prompting

Every recipe that requires environment variables will automatically check for missing values and prompt you interactively. The prompt includes a description and help text explaining how to obtain each value. Values are appended to `.env` so you only need to enter them once.

If `.env` doesn't exist, it's created from `.env.example` on first run.
```

- [ ] **Step 4: Commit**

```bash
git add internal/CLAUDE.md
git commit -m "docs: add cortex deploy, shared minikube, env prompting to CLAUDE.md"
```

---

### Task 5: Manual smoke test

- [ ] **Step 1: Test `_ensure-env` prompting**

Temporarily rename `.env` to `.env.bak`:

```bash
cd /Users/jeffschnitter/git/cli/internal
mv .env .env.bak
```

Run a recipe that requires env vars:

```bash
just test-functional-import
```

Expected: Creates `.env` from `.env.example`, shows "Missing 2 required variable(s): CORTEX_API_KEY, CORTEX_BASE_URL", prompts for each with help text.

Press Ctrl+C after verifying the prompt works. Restore the original `.env`:

```bash
mv .env.bak .env
```

- [ ] **Step 2: Test `_minikube-start`**

Run:

```bash
just _minikube-start
```

Expected: Either "minikube (cortex-minikube) already running" or starts a new cluster with 10GB memory, 4 CPUs, docker driver, and profile name `cortex-minikube`.

- [ ] **Step 3: Test `just help`**

Run:

```bash
just help
```

Expected: All recipes listed. New entries: `cortex-setup`, `cortex-stop`, `cortex-status`, `cortex-pf`, `cortex-db`, `cortex-open`, `minikube-stop`.

- [ ] **Step 4: Test `cortex-setup`**

Run (requires actual env vars set — use real `.env`):

```bash
just cortex-setup
```

Expected: Prompts for any missing vars (GH_USER, GH_PAT, CORTEX_LICENSE_FILE), starts minikube if needed, creates secrets, deploys Cortex via Helm, sets up port forwarding. Frontend at http://localhost:3000, backend at http://localhost:8080.

This takes ~10-15 minutes on first run (image pulls).

- [ ] **Step 5: Test `cortex-status`**

Run:

```bash
just cortex-status
```

Expected: Shows pod status, services, port-forward status.
