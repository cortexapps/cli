# Terraform Solution Design

**Date:** 2026-09-02
**Issue:** CX-43
**Solution tag:** `terraform`

## Overview

A Cortex solution bundle that teaches customers how to manage their Cortex catalog using the [Cortex Terraform provider](https://github.com/cortexapps/terraform-provider-cortex). The solution is hands-on: `cortex solutions install -s terraform` runs a `setup.py` that executes a real `terraform apply`, creating entities in Cortex via Terraform — not via YAML import.

The solution ships:
1. **Working Terraform files** (`_templates/terraform/`) — provider config, teams, domains, services, and a scorecard for Parts Unlimited, the fictional company from *The Phoenix Project*.
2. **Delta files** (`_templates/terraform-delta/`) — modified versions of select `.tf` files demonstrating an incremental update: new service, scorecard promotion, team member added.
3. **`setup.py`** — checks for Terraform CLI, copies files to a working directory, writes `terraform.tfvars`, runs `terraform init` + `terraform apply`.

No `catalog/` or `scorecards/` YAML files. Terraform is the sole source of truth.

---

## Parts Unlimited Org Model

Modeled after Parts Unlimited, the fictional automotive parts retailer from *The Phoenix Project*.

### Teams (4)

| Tag | Name | Description |
|---|---|---|
| `team-development` | Development | Application development (Bill's team) |
| `team-operations` | IT Operations | Infrastructure and operations (Brent's domain) |
| `team-security` | Information Security | Security and compliance (John's team) |
| `team-qa` | Quality Assurance | Testing and QA |

### Domains (2)

| Tag | Name | Services |
|---|---|---|
| `domain-ecommerce` | E-Commerce | `phoenix`, `parts-catalog-api`, `payments-service` |
| `domain-supply-chain` | Supply Chain | `inventory-service`, `ordering-service`, `shipping-service` |

### Services — Initial State (6)

All services start at **Bronze** level on the Production Readiness scorecard. They have descriptions, owner teams, and git configured — but deliberately lack on-call, runbook links, and custom data, so the delta can show meaningful improvement.

| Tag | Name | Owner | Bronze rules met |
|---|---|---|---|
| `phoenix` | The Phoenix Project | `team-development` | description, owner, git |
| `parts-catalog-api` | Parts Catalog API | `team-development` | description, owner, git |
| `payments-service` | Payments Service | `team-development` | description, owner, git |
| `inventory-service` | Inventory Service | `team-operations` | description, owner, git |
| `ordering-service` | Ordering Service | `team-development` | description, owner, git |
| `shipping-service` | Shipping Service | `team-operations` | description, owner, git |

### Scorecard (1)

**Production Readiness** — Bronze/Silver/Gold applied to all services.

| Level | Rules |
|---|---|
| Bronze | Has description, has owner team, has git configured |
| Silver | Has on-call configured, has runbook link, has `terraform-workspace` custom data |
| Gold | Description ≥ 50 characters, has groups set, owned by ≥ 2 teams |

---

## Delta: What Changes

The delta demonstrates three types of Terraform changes in one `terraform apply`:

### File ownership model

Terraform has no requirements on file names — it reads all `.tf` files in a directory and merges them. This means teams can own separate files, submit PRs touching only their file, and the catalog stays decentralized at the file level while remaining centralized in a single repo.

Our demo makes this concrete: `ecommerce.tf` is owned by the e-commerce team, `supply-chain.tf` by the supply chain team. A PR to add a new e-commerce service touches only `ecommerce.tf`. Platform owns `teams.tf` and `scorecards.tf`.

This pattern scales from a handful of services to 100K+ — at extreme scale, customers move to Terraform modules (subdirectories), but the ownership principle is the same.

### 1. Service update — `phoenix` promoted Bronze → Silver
In `_templates/terraform-delta/ecommerce.tf`, the `phoenix` resource gains:
- `oncall` block (fictional PagerDuty policy)
- `links` block with a runbook URL
- `custom_data` block: `terraform-workspace = "phoenix-prod"`

This satisfies all Silver rules. After apply, the scorecard score for `phoenix` updates.

### 2. New service added — `notification-service`
A new `cortex_catalog_entity` resource is added to `ecommerce.tf` for a `notification-service` (owner: `team-development`). Terraform creates it from scratch — no manual API call needed. This is what adding a service looks like in a team's PR.

### 3. Team member added — `team-development`
A new member (`Sarah Connor, sarah.connor@parts-unlimited.com`) is added in `_templates/terraform-delta/teams.tf`. Terraform updates only that resource in place. This is what onboarding someone looks like.

The README instructs the user to run `terraform plan` after copying the delta files to see the diff before applying — specifically calling out which resources show as `~ update` vs `+ create`.

---

## Directory Structure

```
cortexapps_cli/solutions/terraform/
├── README.md
├── setup.py
└── _templates/
    ├── terraform/
    │   ├── provider.tf           # provider config, required versions
    │   ├── variables.tf          # cortex_api_token, cortex_base_url
    │   ├── terraform.tfvars.example
    │   ├── teams.tf              # owned by: platform team
    │   ├── ecommerce.tf          # owned by: e-commerce team (domain + 3 services)
    │   ├── supply-chain.tf       # owned by: supply chain team (domain + 3 services)
    │   └── scorecards.tf         # owned by: platform team
    └── terraform-delta/
        ├── ecommerce.tf          # phoenix → Silver, notification-service added
        └── teams.tf              # new member on team-development
```

---

## setup.py Design

### SETUP_DESCRIPTION

```
"Sets up the Parts Unlimited demo org in your Cortex instance using the Cortex Terraform provider. Requires Terraform >= 1.5 to be installed."
```

### `collect_prompts()`

- `work_dir`: Working directory for Terraform files. Default: `~/parts-unlimited-terraform`. Env var: `TERRAFORM_WORK_DIR`.

API key and base URL are available from the CLI session via `kwargs["cortex_api_key"]` and `kwargs["cortex_base_url"]` — no need to prompt.

### `steps()`

1. **Check Terraform** — runs `terraform version`, fails with a clear message if not found or version < 1.5.
2. **Create working directory** — `mkdir -p {work_dir}`.
3. **Copy Terraform files** — copies all files from `_templates/terraform/` into `{work_dir}`.
4. **Write terraform.tfvars** — writes `cortex_api_token` and `cortex_base_url` into `{work_dir}/terraform.tfvars` (not committed; `.gitignore` entry added).
5. **Write .gitignore** — adds `terraform.tfvars`, `.terraform/`, `*.tfstate*` to `{work_dir}/.gitignore`.
6. **terraform init** — runs `terraform init` in `{work_dir}`.
7. **terraform apply** — runs `terraform apply -auto-approve` in `{work_dir}`.

### `post_steps()`

Prints next-steps message:
- Where the files are (`{work_dir}`)
- How to run the delta: copy `_templates/terraform-delta/` files, run `terraform plan`, then `terraform apply`
- How customers wire this to CI (one-liner pointing to README)

### Error handling

- If Terraform is not installed: print install URL (`https://developer.hashicorp.com/terraform/install`), raise to abort.
- If `terraform init` or `terraform apply` fails: print stderr, raise. State files may be partially created — user can retry from `{work_dir}`.
- `mark_done()` is called after each step so re-runs skip completed steps.

---

## Terraform Files

### `provider.tf`

Declares `cortexapps/cortex` provider `~> 0.6`, Terraform `>= 1.5`. Reads token and base URL from variables.

### `variables.tf`

Two variables: `cortex_api_token` (sensitive, no default) and `cortex_base_url` (default: `https://api.getcortexapp.com`).

### `terraform.tfvars.example`

Template with comments. Instructs user to copy to `terraform.tfvars` and never commit it.

### `teams.tf` (platform-owned)

Four `cortex_catalog_entity` resources (type `team`) with member lists using realistic Parts Unlimited names (Bill, Brent, John, etc.).

### `ecommerce.tf` (e-commerce team-owned)

One `cortex_catalog_entity` resource (type `domain`) for `domain-ecommerce`, followed by three service resources: `phoenix`, `parts-catalog-api`, `payments-service`. Domain and its services co-located — the e-commerce team owns everything in this file.

Services initial state (intentionally Bronze only):
- `description` — short, < 50 chars
- `owner_teams` — `team-development`
- `git` block — fictional repos under `github.com/parts-unlimited/`
- No `oncall`, no `links`, no `custom_data`

### `supply-chain.tf` (supply chain team-owned)

Same pattern: one `domain` resource (`domain-supply-chain`) and three service resources: `inventory-service`, `ordering-service`, `shipping-service`. Owner: `team-operations`.

### `scorecards.tf` (platform-owned)

One `cortex_scorecard` resource: Production Readiness with Bronze/Silver/Gold rules. Filter: `types = ["service"]`.

---

## Scorecard Expression Notes

Cortex Expression Language (CEL-like) rules:

| Level | Rule | Expression |
|---|---|---|
| Bronze | Has description | `entity.description().length > 0` |
| Bronze | Has owner team | `owners.teams.size() > 0` |
| Bronze | Has git configured | `git != null` |
| Silver | Has on-call | `oncall != null` |
| Silver | Has runbook link | `links.exists(l, l.type == "runbook")` |
| Silver | Has terraform-workspace | `customData.exists(d, d.key == "terraform-workspace")` |
| Gold | Description ≥ 50 chars | `entity.description().length >= 50` |
| Gold | Has groups | `groups.size() > 0` |
| Gold | Owned by ≥ 2 teams | `owners.teams.size() >= 2` |

---

## README Structure

```
---
name: Terraform
description: Manage your Cortex catalog as code using the Cortex Terraform provider.
---

# Terraform

## What is the Cortex Terraform provider?
Brief explanation of HCL, providers, and how terraform apply → Cortex API.

## Terraform vs. cortex.yaml — two flavors of GitOps
Centralized (Terraform) vs. decentralized (cortex.yaml per service repo). Neither is better; it depends on who owns the catalog.

## What's Included
- Parts Unlimited demo org: 4 teams, 2 domains, 6 services, 1 scorecard
- Initial state: all services at Bronze on Production Readiness
- Delta: see services improve and a new service appear in one apply

## Prerequisites
- Terraform >= 1.5 (https://developer.hashicorp.com/terraform/install)
- Cortex API key with write access

## Install
`cortex solutions install -s terraform`
(Runs terraform apply. You'll be asked for a working directory.)

## Explore what was created
- Link to Cortex catalog filtered by group `terraform-demo`
- Link to Production Readiness scorecard

## Try the Delta
Step-by-step: copy delta files, terraform plan (shows diff), terraform apply, check scorecard.

## File Walkthrough
One paragraph per .tf file explaining what it does and why.

## Customizing for Your Org
How to adapt: rename entities, add services, extend scorecard rules.

## Next Steps: CI/CD Integration
GitHub Actions snippet that runs terraform plan on PR and terraform apply on merge to main.
Explains that this is the standard customer workflow in practice.
```

---

## Out of Scope

- No `catalog/` or `scorecards/` YAML files — Terraform is the sole source of truth
- No workflows
- No custom entity types or relationship types
- No GitHub Actions templates shipped with the solution (covered in README next steps only)
- Terraform state backend configuration (customers configure their own S3/GCS backend)
- Terraform destroy (not demonstrated; customers handle cleanup)
