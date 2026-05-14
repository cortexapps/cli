# Cortex Minikube Deploy + Shared Cluster Architecture

**Date**: 2026-05-04
**Status**: Draft
**Scope**: `internal/` directory — Justfile, cortex deploy configs, env var prompting

## Problem

The `internal/` Justfile has three minikube-based modules (k8s-agent, SKE, and the new Cortex deploy) that each manage minikube independently with no profile isolation. The customer-experience/minikube project has a working Cortex-on-minikube setup but conflates it with k8s-agent. Additionally, onboarding colleagues requires manually populating `.env` with no guidance on what each var means or how to obtain it.

## Goals

1. Add `cortex-setup` / `cortex-stop` recipes to deploy Cortex locally on minikube
2. All minikube modules share a single cluster via named profile `cortex-minikube`
3. Every recipe that needs env vars uses `_ensure-env` to prompt for missing values with help text
4. Modules are independent but composable (e.g., k8s-agent can target local or cloud Cortex)

## Design

### Shared Minikube Lifecycle

A `MINIKUBE_PROFILE` variable defaulting to `cortex-minikube`, overridable via `.env`:

```
MINIKUBE_PROFILE := env("MINIKUBE_PROFILE", "cortex-minikube")
```

A private `_minikube-start` recipe is the shared entry point:

- Checks if `cortex-minikube` is already running
- If not, starts with `--memory=10240 --cpus=4 --profile=cortex-minikube --driver=docker`
- Sets kubectl context to `cortex-minikube`
- All modules depend on `_minikube-start` instead of managing minikube themselves

A public `minikube-stop` recipe stops the cluster. Individual module `*-stop` recipes only tear down their own Helm releases — they do not stop minikube.

### `_ensure-env` Helper

A private recipe that checks for required env vars, prompts for missing ones, and appends to `.env`.

**Var declaration format** (pipe-delimited, one per argument):

```
NAME|Short label|Help text describing how to obtain the value.
```

**Behavior**:

1. If `.env` does not exist, copy from `.env.example`
2. Source `.env` to load current values
3. Identify which declared vars are empty or absent
4. If none missing, return silently
5. Print summary: `Missing N variables: VAR1, VAR2, VAR3`
6. For each missing var, print label, help text, and prompt:
   ```
   GH_PAT (GitHub PAT for ghcr.io)
     Create at GitHub > Settings > Developer settings > Personal access tokens. Needs read:packages scope.
   : _
   ```
7. Re-prompt if value is blank
8. Append `VAR=value` to `.env`
9. Export into current shell session

**Every recipe that needs env vars** calls `_ensure-env` with its specific var list. This replaces the existing manual `if [ -z "${VAR:-}" ]` checks throughout the Justfile.

### Recipe Structure

```
# Shared infrastructure
_minikube-start              idempotent cluster start
_ensure-env VARS...          check/prompt/populate .env
minikube-stop                stop the shared cluster

# Cortex self-hosted deploy
cortex-setup                 full deploy: secrets, postgres, cortex, port-forward
cortex-stop                  helm uninstall cortex + postgres
cortex-status                pod/svc/port-forward health
cortex-pf                    resume port-forwarding after sleep/reboot
cortex-db                    psql into local postgres
cortex-open                  open http://localhost:3000

# K8s agent (existing, refactored)
k8s-agent-setup              GHCR secret, helm, test manifests, cortex entity
k8s-agent-test               poll Cortex API for test objects
k8s-agent-stop               helm uninstall (keeps cluster)

# SKE (existing, refactored)
ske-setup                    cert-manager, ArgoCD, SKE helm, promise
ske-test                     verify entity type, submit resource, check configmap
ske-stop                     tear down SKE/ArgoCD/cert-manager (keeps cluster)

# Functional tests (existing, add _ensure-env)
test-functional-import       import test data
test-functional              run functional tests

# Axon relay (existing, add _ensure-env)
axon-setup                   start relay containers
axon-stop                    stop relay containers
axon-status                  show relay status
axon-test                    Jenkins + relay end-to-end
axon-echo-setup              echo server smoke test
axon-echo-test               trigger echo workflow
axon-echo-stop               tear down echo

# Prometheus (existing, add _ensure-env)
prometheus-setup             start local prometheus
prometheus-stop              stop prometheus

# Playwright (existing, add _ensure-env)
test-ui                      run Playwright tests
test-workday                 Workday integration tests
```

### Cortex Deploy Details

**New directory**: `internal/cortex/`

| File | Purpose |
|------|---------|
| `values.yaml` | Helm values for `cortex/cortex` chart. Backend 4GB, worker 3GB, frontend defaults. PostgreSQL enabled via chart subchart. Ingress disabled — port-forward only. |
| `.gitkeep` | Placeholder (values.yaml is the only committed file) |

**`cortex-setup` flow**:

1. `_ensure-env` for `GH_USER`, `GH_PAT`, `CORTEX_LICENSE_FILE`
2. `_minikube-start`
3. Create GHCR pull secret (`cortex-docker-registry-secret`) from `GH_USER` + `GH_PAT`
4. Create `cortex-secret` with DB creds + license JWT (read from `CORTEX_LICENSE_FILE`)
5. `helm repo add cortex https://helm-charts.cortex.io && helm repo update`
6. `helm upgrade --install cortex cortex/cortex --values cortex/values.yaml --timeout 15m --wait`
7. Wait for frontend + backend pods ready
8. Kill existing port-forwards, start new ones (frontend :3000, backend :8080)
9. Print status + URLs

**`cortex-stop`**: `helm uninstall cortex`, kill port-forwards. Does not stop minikube.

**`cortex-pf`**: Kill + restart port-forwards (for after sleep/reboot).

**`cortex-db`**: `kubectl exec` into the postgres pod with `psql`.

**`cortex-status`**: Show pod status, service endpoints, port-forward PIDs.

### K8s-Agent Refactoring

Changes to existing `k8s-agent-setup`:
- Add `_ensure-env` call for `GH_USER`, `GITHUB_TOKEN`, `CORTEX_API_KEY`, `CORTEX_BASE_URL`
- Replace inline `minikube status`/`minikube start` with dependency on `_minikube-start`
- Add `--profile ${MINIKUBE_PROFILE}` to any remaining minikube commands
- No functional changes to what it deploys

Changes to `k8s-agent-stop`:
- Remove `minikube stop` — only `helm uninstall`
- Add `--profile` flag if any minikube commands remain

### SKE Refactoring

Changes to existing `ske-setup`:
- Add `_ensure-env` call for `SKE_LICENSE_TOKEN`, `CORTEX_API_KEY`, `CORTEX_BASE_URL`, `GH_USER`, `GITHUB_TOKEN`
- Replace inline minikube start with dependency on `_minikube-start`
- Add `--profile ${MINIKUBE_PROFILE}` to `minikube image load`

Changes to `ske-stop`:
- Remove `minikube stop` — only tear down SKE/ArgoCD/cert-manager
- Add `--profile` flag if any minikube commands remain

### Existing Recipe Retrofits

Every recipe that currently does manual env var checking gets converted to `_ensure-env`. The var lists per recipe:

| Recipe | Required vars |
|--------|--------------|
| `test-functional-import`, `test-functional` | `CORTEX_API_KEY`, `CORTEX_BASE_URL` |
| `axon-setup` | `CORTEX_API_KEY` (integration-specific vars stay optional with current conditional logic) |
| `axon-test` | `CORTEX_API_KEY` |
| `axon-echo-setup` | `CORTEX_API_KEY` |
| `axon-echo-test` | `CORTEX_API_KEY`, `CORTEX_BASE_URL` |
| `prometheus-setup` | (none — no env vars needed) |
| `test-ui` | `CORTEX_APP_URL`, `CORTEX_TENANT_CODE`, `GOOGLE_EMAIL`, `GOOGLE_PASSWORD`, `GOOGLE_TOTP_URI` |
| `test-workday` | `CORTEX_APP_URL`, `CORTEX_TENANT_CODE`, `GOOGLE_EMAIL`, `GOOGLE_PASSWORD`, `GOOGLE_TOTP_URI`, `WORKDAY_USERNAME`, `WORKDAY_PASSWORD`, `WORKDAY_OWNERSHIP_REPORT_URL` |

Note: `axon-setup` has optional integration-specific vars (GITHUB_TOKEN, GITLAB_TOKEN, etc.) that control which services start. These stay as-is with the existing conditional logic — `_ensure-env` only covers the hard requirements.

### Env Var Reference (new vars only)

| Variable | Description | Help text |
|----------|-------------|-----------|
| `MINIKUBE_PROFILE` | Minikube profile name (default: `cortex-minikube`) | Override if you already have a profile with this name. Most people can leave this at the default. |
| `GH_PAT` | GitHub PAT for ghcr.io image pulls | Create at GitHub > Settings > Developer settings > Personal access tokens. Needs `read:packages` scope for pulling Cortex container images. |
| `CORTEX_LICENSE_FILE` | Path to Cortex license JWT file | Get from 1Password vault 'Cortex Licenses' or ask in #engineering Slack channel. Save the file anywhere and provide the absolute path. |

### `.env.example` Updates

Add to the Cortex self-hosted section:

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
GH_PAT=

# Absolute path to your Cortex license JWT file.
CORTEX_LICENSE_FILE=
```

### `CLAUDE.md` Updates

Add a "Cortex self-hosted deploy" section to `internal/CLAUDE.md` documenting:
- The `cortex-setup` / `cortex-stop` / `cortex-pf` recipes
- Required env vars
- How to use k8s-agent with local Cortex (`CORTEX_BASE_URL=http://cortex-backend-service:80`)
- The shared minikube profile

Update the existing k8s-agent and SKE sections to note the shared profile.

## Out of Scope

- Resource profiles (minimal/small/medium/large) — fixed at 10GB/4CPU for simplicity
- ArgoCD-based Cortex deployment mode — direct Helm + port-forward only
- Ingress / DNS configuration — port-forward is sufficient for local dev
- Automated testing of the Cortex deploy itself (health checks are in `cortex-status`)
