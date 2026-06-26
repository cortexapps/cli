# internal/ — Non-public tooling for Cortex CLI

This directory contains internal test infrastructure, integration tests, and development tools that are **not published** with the CLI. It has its own Justfile, .env, and pytest config separate from the root project.

## Quick reference

```bash
cd internal/

# See all available recipes
just

# Shared minikube cluster
just minikube-stop            # stop the shared cluster (all modules)

# Cortex self-hosted deploy
just cortex-setup             # deploy Cortex on minikube
just cortex-stop              # tear down Cortex (keeps cluster)
just cortex-status            # show pod/port-forward status
just cortex-pf                # resume port forwarding after sleep
just cortex-db                # psql into local postgres
just cortex-open              # open http://localhost:3000

# Run functional tests
just test-functional-import   # prerequisite: loads test data
just test-functional          # run all functional tests

# SKE (Syntasso Kratix Enterprise)
just ske-setup                # install ArgoCD + SKE, deploy Promise
just ske-test                 # verify end-to-end: Cortex Entity Type → Git → K8s
just ske-stop                 # tear down SKE/ArgoCD/cert-manager (keeps cluster)

# K8s agent
just k8s-agent-setup          # deploy k8s-agent + test objects
just k8s-agent-test           # verify test objects appear in Cortex
just k8s-agent-stop           # tear down k8s-agent (keeps cluster)

# Axon relay
just axon-setup               # start relay containers for configured integrations
just axon-test                # set up Jenkins + relay end-to-end
just axon-echo-setup          # simple echo server relay smoke test
```

## Environment

- **`.env`** — active config (gitignored). Copy from `.env.example` and fill in values.
- **`set dotenv-load` + `set export`** in Justfile means all `.env` vars are auto-loaded and exported.

### Environment profiles

Switch between cloud and local dev with `just env`:

```bash
just env            # switch to cloud workspace (.env.default)
just env local      # switch to local dev (.env.local)
just env-show       # show active profile and key vars
```

Profile files (`.env.<name>`) contain only the vars that differ per environment (API key, base URL, app URL, tenant code). `just env` patches those into `.env` — shared vars are untouched.

Setup:
1. Copy `.env.default.example` → `.env.default` and fill in your cloud workspace values
2. Copy `.env.local.example` → `.env.local` and fill in your local API key (from `~/.cortex/config [cortex-local]`)
- **`PYTHONPATH=..:../tests`** is set in pytest commands so internal tests can import both `cortexapps_cli` and `helpers.utils` from the parent project.

## Env var prompting

Every recipe that requires environment variables will automatically check for missing values and prompt you interactively. The prompt includes a description and help text explaining how to obtain each value. Values are appended to `.env` so you only need to enter them once.

If `.env` doesn't exist, it's created from `.env.example` on first run.

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

## Directory structure

```
internal/
├── CLAUDE.md              # this file
├── Justfile               # all recipes (cortex deploy, k8s-agent, SKE, axon, tests)
├── .env                   # local secrets (gitignored)
├── .env.example           # template with all required vars
├── pytest.ini             # local pytest config (avoids root pytest.ini interference)
├── tests/                 # functional tests (moved from tests/functional/)
├── cortex/                # Cortex Helm values for minikube deploy
├── k8s/                   # k8s-agent helm chart, test manifests, Cortex entity
├── axon/                  # relay compose files, accept.json configs, Jenkins setup
├── prometheus/            # local Prometheus compose + config
├── ui/                    # Playwright UI tests
└── ske/                   # SKE + Cortex integration test
    ├── FLOW.md            # mermaid diagrams showing the integration flow
    ├── promise.yaml       # ConfigMap Promise (Kind: Message, Group: demo.cortex.io)
    ├── example-resource.yaml  # sample Message resource request
    ├── values.yaml        # Helm values for SKE operator
    ├── argocd-app.yaml    # ArgoCD Application watching the GitOps repo
    └── workflows/         # Kratix pipeline (Dockerfile + Python script)
```

## SKE integration — what you need to know

### Key concepts

- **SKE Promise** = a service template that defines an API (CRD) + a pipeline to fulfill requests
- **SKE Cortex Controller** = watches for Promises labeled `kratix.io/cortex: "true"` and auto-creates Entity Types + Workflows in Cortex
- **Kratix Destination + GitStateStore** = tells Kratix where to write pipeline outputs (a Git repo)
- **ArgoCD** = GitOps tool that syncs manifests from the Git repo to the K8s cluster (both directions: resource requests in, pipeline outputs out)

### The flow

1. Platform team applies a Promise → SKE Cortex Controller creates Entity Type + Workflows in Cortex
2. Developer triggers a workflow in Cortex → Cortex commits resource request YAML to Git repo
3. ArgoCD syncs the resource request to the cluster → Kratix runs the pipeline
4. Pipeline writes K8s manifests to Git → ArgoCD syncs them back to cluster → resource is created

### Critical gotchas discovered during setup

- **cert-manager is required** — SKE needs it for TLS certificates. Must be installed before the SKE Helm chart.
- **Don't create the GHCR pull secret manually** — The SKE Helm chart creates `syntasso-registry` from the `skeLicense` value. Manual creation causes an ownership conflict.
- **SKE version "latest" is the safe default** — Specific version tags (like v0.99.0 from docs) may not exist. The Helm chart defaults to `"latest"` which resolves to the actual latest (e.g. v0.45.0).
- **GitStateStore + Destination must be created** — Kratix won't know where to write pipeline outputs without these. The setup recipe creates them pointing to the same GitHub repo ArgoCD watches.
- **git-credentials secret** — Kratix needs this to push pipeline outputs to Git. Created from `GH_USER` + `GITHUB_TOKEN`.
- **SKE auto-creates the Destination** — When SKE detects a GitStateStore named `default`, it creates a Destination called `local-cluster` automatically. Don't create your own Destination — it will conflict.
- **cert-manager webhook needs extra time** — Deployments report "available" before the webhook CA certificate is populated. Wait for `caBundle` in the ValidatingWebhookConfiguration before running Helm.
- **`integrationAlias` must match your Cortex GitHub integration** — Check with `poetry run cortex integrations get-all | jq '.configurations[] | select(.type == "github")'`. Ours is `cortex-prod`.
- **Auto-generated workflows have `isRunnableViaApi: false`** — You cannot trigger them via the Cortex REST API. They must be triggered from the Cortex UI, or you can commit the resource request YAML directly to the Git repo.
- **ArgoCD server-side apply** — Required for ArgoCD CRD installation because annotations exceed the 262KB client-side limit. Use `kubectl apply --server-side`.
- **ArgoCD sync interval is ~3 minutes** — After a commit to the Git repo, ArgoCD may take up to 3 minutes to detect and sync. The pipeline output → final resource step has this latency.
- **After changing Helm values, restart the cortex controller** — `helm upgrade` alone may not pick up config changes in the cortex controller. Delete the pod: `kubectl delete pod -n kratix-platform-system -l app=ske-cortex-controller`

### Environment variables for SKE

| Variable | Description |
|----------|-------------|
| `SKE_LICENSE_TOKEN` | Syntasso license (ghp_-prefixed GitHub PAT, also used for GHCR pulls) |
| `CORTEX_API_KEY` | Cortex API key (passed to SKE Cortex Controller) |
| `CORTEX_BASE_URL` | Cortex API URL |
| `GH_USER` | GitHub username for git-credentials secret |
| `GITHUB_TOKEN` | GitHub PAT for git-credentials secret |

### GitOps repo

- **Repo**: `jeff-test-org/ske-test-resources` (public)
- **`kratix-resource-requests/`** — where Cortex workflows commit resource request YAMLs
- **`kratix-output/`** — where Kratix pipelines write output manifests
- ArgoCD watches the entire repo with `directory.recurse: true`

### Useful debugging commands

```bash
# Check all Kratix components are running
kubectl get pods -n kratix-platform-system

# Check Promise status
kubectl get promise message -o yaml

# Check Message resource status
kubectl get message -A -o yaml

# Check pipeline pods (look for recent ones)
kubectl get pods -n default --sort-by=.metadata.creationTimestamp | grep kratix

# Check pipeline pod logs
kubectl logs -n default <pipeline-pod-name>

# Check ArgoCD sync status
kubectl get application kratix-cortex-resources -n argocd

# Check what's in the GitOps repo
gh api repos/jeff-test-org/ske-test-resources/git/trees/main?recursive=1 --jq '.tree[].path'

# Check the ConfigMap was created
kubectl get configmap ske-test-msg -n default -o yaml

# Verify Cortex integration alias
poetry run cortex integrations get-all | jq '.configurations[] | select(.type == "github")'

# Force ArgoCD to sync now (instead of waiting 3 min)
kubectl -n argocd exec deploy/argocd-server -- argocd app sync kratix-cortex-resources --insecure
```
