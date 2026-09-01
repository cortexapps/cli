---
name: Monorepo
description: Model a real monorepo in Cortex — five Cortex services mapped to subdirectories of a single public GitHub repo, each scoped by basePath.
---

# Monorepo

This solution demonstrates the monorepo pattern in Cortex using mock services inside the [`cortexapps/cli`](https://github.com/cortexapps/cli) repo. Five Cortex service entities each map to their own subdirectory under `cortexapps_cli/solutions/monorepo/services/`, complete with a `cortex.yaml`, a `README.md`, and mock source code. Each entity sees only the commits, PRs, and files in its own directory.

```
  https://github.com/cortexapps/cli/tree/main/cortexapps_cli/solutions/monorepo/services
  ════════════════════════════════════════════════════════════════════════
  │
  ├── cli-core/                 ──►  ┌─────────────────────────────────┐
  │                                  │  monorepo-demo-cli-core         │
  │                                  │  Core CLI package               │
  │                                  │  src/cli.py                     │
  │                                  └─────────────────────────────────┘
  │
  ├── cli-commands/             ──►  ┌─────────────────────────────────┐
  │                                  │  monorepo-demo-cli-commands     │
  │                                  │  Command implementations        │
  │                                  │  src/commands.py                │
  │                                  └─────────────────────────────────┘
  │
  ├── cli-solutions/            ──►  ┌─────────────────────────────────┐
  │                                  │  monorepo-demo-cli-solutions    │
  │                                  │  Solutions framework            │
  │                                  │  src/solutions.py               │
  │                                  └─────────────────────────────────┘
  │
  ├── cli-tests/                ──►  ┌─────────────────────────────────┐
  │                                  │  monorepo-demo-cli-tests        │
  │                                  │  Integration test suite         │
  │                                  │  src/test_cli.py                │
  │                                  └─────────────────────────────────┘
  │
  └── cli-docker/               ──►  ┌─────────────────────────────────┐
                                     │  monorepo-demo-cli-docker       │
                                     │  Container infrastructure       │
                                     │  Dockerfile                     │
                                     └─────────────────────────────────┘
```

Each service directory has this structure:

```
services/
└── cli-core/
    ├── cortex.yaml      ← Cortex entity definition (GitOps discoverable)
    ├── README.md        ← Service documentation
    └── src/
        └── cli.py       ← Mock source code
```

Each entity is defined like this (the `x-cortex-git` block lives under `info:`):

```yaml
info:
  x-cortex-tag: monorepo-demo-cli-core
  x-cortex-git:
    github:
      alias: cortex-cli        # only needed with multiple GitHub integrations, and your repo isn't under the default
      repository: cortexapps/cli
      basePath: cortexapps_cli/solutions/monorepo/services/cli-core
```

All five entities are tagged with the group `monorepo-demo` for easy catalog filtering.

## What's Included

**5 service entities** (group: `monorepo-demo`)

| Tag | basePath | Description |
|---|---|---|
| `monorepo-demo-cli-core` | `services/cli-core` | Core CLI — Typer app, HTTP client, config, utils |
| `monorepo-demo-cli-commands` | `services/cli-commands` | Command implementations per Cortex resource |
| `monorepo-demo-cli-solutions` | `services/cli-solutions` | Solutions framework — installable bundles |
| `monorepo-demo-cli-tests` | `services/cli-tests` | Integration test suite against live Cortex API |
| `monorepo-demo-cli-docker` | `services/cli-docker` | Container infra — published `cortexapp/cli` image |

> Full basePaths are prefixed with `cortexapps_cli/solutions/monorepo/` — shortened above for readability.

**1 scorecard** — `monorepo-component-health` — Bronze/Silver/Gold:
- Bronze: has description + git configured with basePath
- Silver: belongs to at least one group
- Gold: verified within 90 days

**5 `cortex.yaml` files** committed into the repo — one per component — so GitOps discovers them automatically once GitHub is connected.

## Installation

```
cortex solutions install -s monorepo
cortex solutions post-install -s monorepo
```

The install step creates all 5 entities and the scorecard immediately. The post-install step configures the `cortex-cli` GitHub integration (PAT) so Cortex can read the repo.

## After Installing

**Create a catalog**

1. Go to [Catalogs](https://app.getcortexapp.com/admin/catalogs) → **New Catalog**
2. Name it **Monorepo Demo**
3. Set the catalog filter:
   - **Entity type:** `service`
   - **Advanced options → Groups → Include:** `monorepo-demo`

> Catalog creation will be automated once catalog API support is added to the CLI.

## GitOps Auto-Discovery

Once the `cortex-cli` integration is set up, add the repo in Cortex → **Settings → GitOps**:

```
Repository: cortexapps/cli
```

Cortex will find the five `cortex.yaml` files and keep entities in sync with any changes pushed to the repo:

```
cortexapps_cli/solutions/monorepo/services/cli-core/cortex.yaml       →  monorepo-demo-cli-core
cortexapps_cli/solutions/monorepo/services/cli-commands/cortex.yaml   →  monorepo-demo-cli-commands
cortexapps_cli/solutions/monorepo/services/cli-solutions/cortex.yaml  →  monorepo-demo-cli-solutions
cortexapps_cli/solutions/monorepo/services/cli-tests/cortex.yaml      →  monorepo-demo-cli-tests
cortexapps_cli/solutions/monorepo/services/cli-docker/cortex.yaml     →  monorepo-demo-cli-docker
```

## Testing GitOps

To see GitOps discovery in action, delete one or more entities and let Cortex recreate them from the `cortex.yaml` files in the repo.

**Step 1 — Delete an entity (or all of them):**

```bash
# Delete a single entity
cortex catalog delete --tag monorepo-demo-cli-core --force

# Or delete all five at once
cortex catalog delete --tag monorepo-demo-cli-core --force
cortex catalog delete --tag monorepo-demo-cli-commands --force
cortex catalog delete --tag monorepo-demo-cli-solutions --force
cortex catalog delete --tag monorepo-demo-cli-tests --force
cortex catalog delete --tag monorepo-demo-cli-docker --force
```

**Step 2 — Configure GitOps (if not already done):**

1. Go to **Settings → GitOps** in the Cortex UI
2. Click **Add Repository**
3. Enter `cortexapps/cli` and select the `cortex-cli` integration
4. Save — Cortex will immediately scan the repo for `cortex.yaml` files

**Step 3 — Trigger a sync:**

GitOps syncs automatically on each push to the repo. To trigger a manual sync without pushing:

1. Go to **Catalogs → All Entities**
2. Click **Import Entities → Import Manually**
3. Select **GitHub**
4. Follow the prompts to select the `cortexapps/cli` repository

Cortex will find the `cortex.yaml` files in each subdirectory and recreate the deleted entities exactly as defined — group, git basePath, description, and all.

## Adapting for Your Own Monorepo

1. Add a `cortex.yaml` to each component subdirectory in your repo
2. Set `x-cortex-git.github.repository` and `basePath` for each component
3. Add `x-cortex-git.github.alias` if you have more than one GitHub integration configured and your repo isn't under the default
4. Add a consistent group tag to all components (e.g. `my-monorepo`)
5. Add GitOps → your repo in Cortex Settings
6. Cortex discovers and syncs all components automatically

The `basePath` is what splits one repo into many scoped entities — each service sees only the activity in its own directory.
