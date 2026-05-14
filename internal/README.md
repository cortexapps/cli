# internal/ — Cortex CLI Internal Tooling

Non-public test infrastructure, integration tests, and development tools for the [Cortex CLI](https://github.com/cortexapps/cli). Nothing in this directory is published with the CLI package.

## Prerequisites

- **Python 3.11+** and [Poetry](https://python-poetry.org/docs/#installation)
- [just](https://github.com/casey/just#installation) — task runner (like `make` but simpler)
- [Docker](https://docs.docker.com/get-docker/) — for Axon relay, Jenkins, and Prometheus
- [minikube](https://minikube.sigs.k8s.io/docs/start/) — for k8s-agent and SKE tests
- [Helm](https://helm.sh/docs/intro/install/) — for k8s-agent and SKE installs
- [GitHub CLI](https://cli.github.com/) (`gh`) — for repo operations and SKE GitOps

## Getting started

```bash
# 1. Clone the repo and install dependencies
git clone git@github.com:cortexapps/cli.git
cd cli
poetry install

# 2. Set up your environment
cd internal
cp .env.example .env
# Edit .env and fill in your API keys and tokens (see comments in the file)

# 3. See what's available
just
```

Running `just` with no arguments lists all available recipes and a short description of each.

## Manual setup (one-time)

Before running tests, configure these in your Cortex tenant:

- **GitHub integration** — Settings > Integrations > GitHub. Note the alias for your `.env` file.
- **GitLab integration** — Settings > Integrations > GitLab. Note the alias for your `.env` file.
- **GitHub test organization** — A dedicated org (not production). Add a custom property `cortex-cli-functional-test` as a safety marker to prevent accidental use of production orgs.

To verify your GitHub integration alias:

```bash
poetry run cortex integrations get-all | jq '.configurations[] | select(.type == "github")'
```

## What's in here

| Directory | What it does | Key recipes |
|-----------|-------------|-------------|
| `tests/` | Functional tests against real Cortex API (GitHub, GitLab integrations) | `just test-functional` |
| `k8s/` | K8s-agent integration test (deploys agent to minikube, verifies data in Cortex) | `just k8s-agent-setup`, `just k8s-agent-test` |
| `axon/` | Axon relay tests (GitHub, GitLab, Jira, Jenkins, etc.) | `just axon-setup`, `just axon-test` |
| `prometheus/` | Local Prometheus instance for relay testing | `just prometheus-setup` |
| `ui/` | Playwright browser tests against Cortex web app | `just test-ui` |
| `ske/` | SKE (Syntasso Kratix Enterprise) + Cortex integration test | `just ske-setup`, `just ske-test` |

## Environment variables

All configuration lives in `.env`. The file is gitignored — your secrets stay local.

The `.env.example` file documents every variable with comments explaining what it's for, where to get it, and which tests need it. You only need to fill in the sections for the tools you plan to use.

At minimum, most recipes need:

| Variable | Required for |
|----------|-------------|
| `CORTEX_API_KEY` | Everything |
| `CORTEX_BASE_URL` | Everything (defaults to `https://api.getcortexapp.com`) |
| `GITHUB_TOKEN` | Functional tests, k8s-agent, SKE |
| `GH_USER` | k8s-agent, SKE |

## Common workflows

### Functional tests

```bash
# Load test data first (one-time prerequisite)
just test-functional-import

# Run all functional tests
just test-functional

# Run a specific test file
just test-functional tests/test_gh_branches.py
```

### K8s agent

```bash
just k8s-agent-setup    # starts minikube, deploys agent + test objects
just k8s-agent-test     # polls Cortex until test objects appear
just k8s-agent-stop     # tears down everything
```

### SKE + Cortex integration

```bash
just ske-setup    # starts minikube, installs ArgoCD + cert-manager + SKE, deploys Promise
just ske-test     # verifies Entity Type, Workflows, and ConfigMap creation end-to-end
just ske-stop     # tears down everything + stops minikube
```

See `ske/FLOW.md` for diagrams showing how the integration works.

### Axon relay

```bash
just axon-setup         # starts relay containers for all configured integrations
just axon-status        # check running containers
just axon-stop          # stop all relay containers

# Jenkins end-to-end test
just axon-test          # sets up Jenkins + relay + workflow
just axon-test-stop     # tears down Jenkins + relay

# Echo server smoke test
just axon-echo-setup    # starts echo server + relay
just axon-echo-test     # triggers workflow and verifies completion
just axon-echo-stop     # tears down echo server + relay
```

## Troubleshooting

- **"CORTEX_API_KEY is required"** — Make sure `.env` exists and has the key set. The Justfile auto-loads it.
- **minikube tests fail** — Check `minikube status`. If it's stopped, the setup recipe will start it. If it's broken, `minikube delete && minikube start` is the nuclear option.
- **Functional tests fail with "Invalid configuration alias"** — Verify your integration alias matches what's in Cortex: `poetry run cortex integrations get-all | jq '.configurations[]'`
- **Docker containers won't start** — Make sure Docker Desktop is running. Check logs with `docker compose -f <compose-file> logs`.
