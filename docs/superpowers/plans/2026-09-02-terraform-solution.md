# Terraform Solution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `terraform` Cortex solution bundle that lets users run `cortex solutions post-install -s terraform` to apply a real `terraform apply`, creating a Parts Unlimited demo org in their Cortex instance.

**Architecture:** A setup.py script checks for the Terraform CLI, copies `.tf` template files to a working directory, writes credentials to `terraform.tfvars`, and runs `terraform init` + `terraform apply`. No YAML catalog files — Terraform is the sole source of truth. A `_templates/terraform-delta/` directory contains modified `.tf` files users can drop in to trigger a second apply that promotes a service from Bronze to Silver on the Production Readiness scorecard.

**Tech Stack:** Python 3.11+, HCL (Terraform), `cortexapps/cortex` Terraform provider `~> 0.6`, `subprocess` for shell invocation, `SolutionSetup` base class from `cortexapps_cli.solutions._lib.setup_base`.

**Spec:** `docs/superpowers/specs/2026-09-02-terraform-solution-design.md`

## Global Constraints

- Terraform provider: `cortexapps/cortex ~> 0.6`, Terraform CLI `>= 1.5`
- Entity tags: kebab-case (`team-development`, `phoenix`, `domain-ecommerce`)
- All entities tagged with group `terraform-demo` for easy filtering/cleanup
- No `catalog/` or `scorecards/` YAML files — Terraform only
- No `on_call` rules in scorecard — demo must work without external integrations (PagerDuty etc.)
- setup.py entry point: `main(**kwargs)` — `kwargs["cortex_api_key"]` and `kwargs["cortex_base_url"]` come from CLI session
- setup.py run via: `cortex solutions post-install -s terraform`
- State file: `~/.cortex/solutions/terraform.json` (managed by SolutionSetup base class)
- `mark_done()` / `already_done()` used for every step so re-runs skip completed steps
- Parts Unlimited theme throughout — characters from *The Phoenix Project* (Bill, Brent, John)
- Services intentionally start at Bronze only (no links, no metadata) so delta is meaningful

---

## File Map

| File | Action | Purpose |
|---|---|---|
| `cortexapps_cli/solutions/terraform/README.md` | Create | Solution README with frontmatter, full docs, delta walkthrough |
| `cortexapps_cli/solutions/terraform/setup.py` | Create | Post-install script: terraform check → copy → tfvars → init → apply |
| `cortexapps_cli/solutions/terraform/_templates/terraform/provider.tf` | Create | Terraform provider config |
| `cortexapps_cli/solutions/terraform/_templates/terraform/variables.tf` | Create | Input variables for token and base URL |
| `cortexapps_cli/solutions/terraform/_templates/terraform/terraform.tfvars.example` | Create | Template tfvars with comments |
| `cortexapps_cli/solutions/terraform/_templates/terraform/teams.tf` | Create | 4 team entities (Development, Operations, Security, QA) |
| `cortexapps_cli/solutions/terraform/_templates/terraform/ecommerce.tf` | Create | domain-ecommerce + 3 Bronze services (phoenix, parts-catalog-api, payments-service) |
| `cortexapps_cli/solutions/terraform/_templates/terraform/supply-chain.tf` | Create | domain-supply-chain + 3 Bronze services (inventory, ordering, shipping) |
| `cortexapps_cli/solutions/terraform/_templates/terraform/scorecards.tf` | Create | Production Readiness scorecard (Bronze/Silver/Gold) |
| `cortexapps_cli/solutions/terraform/_templates/terraform-delta/ecommerce.tf` | Create | ecommerce.tf with phoenix → Silver + notification-service added |
| `cortexapps_cli/solutions/terraform/_templates/terraform-delta/teams.tf` | Create | teams.tf with Sarah Connor added to team-development |

---

## Task 1: Scaffold solution directory and README

**Files:**
- Create: `cortexapps_cli/solutions/terraform/README.md`

**Interfaces:**
- Produces: `cortexapps_cli/solutions/terraform/` directory; `cortex solutions list` will show "Terraform" entry; `cortex solutions info -s terraform` will show the README body

- [ ] **Step 1: Create the solution directory**

```bash
mkdir -p cortexapps_cli/solutions/terraform/_templates/terraform
mkdir -p cortexapps_cli/solutions/terraform/_templates/terraform-delta
```

- [ ] **Step 2: Write README.md**

Create `cortexapps_cli/solutions/terraform/README.md` with this exact content:

````markdown
---
name: Terraform
description: Manage your Cortex catalog as code using the Cortex Terraform provider.
---

# Terraform

The [Cortex Terraform provider](https://github.com/cortexapps/terraform-provider-cortex) lets you define your entire service catalog — teams, services, domains, scorecards — as HCL code in `.tf` files. Changes go through PR review and apply automatically on merge, giving you a fully auditable, GitOps-driven catalog.

## What is HCL?

HCL (HashiCorp Configuration Language) is the declarative language used in `.tf` files. It reads like structured config rather than code:

```hcl
resource "cortex_catalog_entity" "phoenix" {
  tag         = "phoenix"
  name        = "The Phoenix Project"
  description = "Main e-commerce monolith for Parts Unlimited."

  owners = [{ name = "team-development", type = "group", provider = "CORTEX" }]

  git = {
    github = { repository = "parts-unlimited/phoenix" }
  }
}
```

Terraform reads all `.tf` files in a directory, compares them to the current live state, and applies only what changed.

## Terraform vs. cortex.yaml — two flavors of GitOps

Both approaches keep your catalog in git and apply changes on merge. The difference is where the files live:

| | Terraform | cortex.yaml |
|---|---|---|
| **Files live in** | One central infra repo | Each service's own repo |
| **Managed by** | Platform / infra team | Individual service teams |
| **Also manages** | AWS, GCP, everything else | Just Cortex catalog |
| **Apply mechanism** | CI runs `terraform apply` | Cortex git integration polls files |

Neither is better. Platform teams who already manage cloud infrastructure with Terraform often prefer the centralized approach. Dev teams who want catalog config alongside their code prefer cortex.yaml.

## File ownership at scale

Terraform has no requirements on file names — it reads all `.tf` files in a directory and merges them. This means you can split by team or domain ownership:

```
infra-catalog/
├── provider.tf          ← platform team
├── teams.tf             ← platform team
├── scorecards.tf        ← platform team
├── ecommerce.tf         ← e-commerce team (domain + services)
├── supply-chain.tf      ← supply chain team (domain + services)
└── payments.tf          ← payments team
```

Each team submits PRs touching only their file. At very large scale (100K+ services), teams use Terraform modules (subdirectories) to organize further — but the ownership model is the same.

## What's Included

This solution installs a demo org for **Parts Unlimited** (from *The Phoenix Project*):

- **4 teams**: Development (Bill's team), IT Operations (Brent's domain), Information Security (John's team), QA
- **2 domains**: E-Commerce, Supply Chain
- **6 services**: The Phoenix Project, Parts Catalog API, Payments Service, Inventory Service, Ordering Service, Shipping Service
- **1 scorecard**: Production Readiness (Bronze/Silver/Gold)

All services start at **Bronze** — intentionally incomplete so you can see the delta in action.

## Prerequisites

- Terraform >= 1.5 — install at https://developer.hashicorp.com/terraform/install
- Cortex API key with write access

## Install

```bash
cortex solutions post-install -s terraform
```

You'll be asked where to create the working directory (default: `~/parts-unlimited-terraform`). The script will:
1. Verify Terraform is installed
2. Copy the `.tf` files to your working directory
3. Write your credentials to `terraform.tfvars`
4. Run `terraform init` to download the Cortex provider
5. Run `terraform apply` to create all entities in Cortex

## Explore what was created

After install, browse your Cortex catalog filtered by the `terraform-demo` group to see all created entities. Open the **Production Readiness** scorecard to see all 6 services at Bronze.

## Try the Delta

The delta shows what a real team PR looks like — modify a file, plan, apply, watch the scorecard update.

**Step 1: Copy the delta files into your working directory**

```bash
cp <solutions-templates>/terraform-delta/ecommerce.tf ~/parts-unlimited-terraform/ecommerce.tf
cp <solutions-templates>/terraform-delta/teams.tf ~/parts-unlimited-terraform/teams.tf
```

> The delta files are in `_templates/terraform-delta/` inside the installed solutions package. Run `cortex solutions info -s terraform` to find the exact path.

**Step 2: See what will change**

```bash
cd ~/parts-unlimited-terraform
terraform plan
```

You'll see:
- `~ cortex_catalog_entity.phoenix` — **update** (adds links, metadata)
- `+ cortex_catalog_entity.notification_service` — **create** (new service)
- `~ cortex_catalog_entity.team_development` — **update** (new team member)

**Step 3: Apply**

```bash
terraform apply
```

**Step 4: Check the scorecard**

Open Production Readiness in Cortex. The Phoenix Project should now show **Silver**.

## File Walkthrough

**`provider.tf`** — Declares the `cortexapps/cortex` provider version and reads credentials from variables. This is the only file that changes if you upgrade the provider version.

**`variables.tf`** — Defines `cortex_api_token` (sensitive) and `cortex_base_url`. Values come from `terraform.tfvars` (never committed) or environment variables (`CORTEX_API_TOKEN`, `CORTEX_API_URL`).

**`teams.tf`** — Owned by the platform team. Defines all teams and their members. Changes here require a platform PR.

**`ecommerce.tf`** — Owned by the e-commerce team. Defines the E-Commerce domain and its three services. Changes here — new services, updated descriptions, added links — are the e-commerce team's PR to make.

**`supply-chain.tf`** — Same pattern, owned by the supply chain team.

**`scorecards.tf`** — Owned by the platform team. Defines the Production Readiness scorecard and its Bronze/Silver/Gold rules.

## Customizing for Your Org

1. Rename entity tags and display names throughout
2. Replace `parts-unlimited/*` GitHub repos with your actual repos
3. Add more services: copy any service block from `ecommerce.tf` and adjust the tag, name, and owner
4. Extend scorecard rules: add rules to `scorecards.tf` with the expression language shown in the [Cortex docs](https://docs.cortex.io/docs/reference/scorecard-rules)
5. Split into more files as your team grows — Terraform reads them all

## Next Steps: CI/CD Integration

In practice, customers commit their `.tf` files to a repo and let CI handle applies. Here's a minimal GitHub Actions workflow:

```yaml
# .github/workflows/cortex-catalog.yml
name: Cortex Catalog

on:
  pull_request:
    paths: ['catalog/**']
  push:
    branches: [main]
    paths: ['catalog/**']

jobs:
  plan:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "~> 1.5"
      - run: terraform init
        working-directory: catalog
        env:
          TF_VAR_cortex_api_token: ${{ secrets.CORTEX_API_TOKEN }}
      - run: terraform plan
        working-directory: catalog
        env:
          TF_VAR_cortex_api_token: ${{ secrets.CORTEX_API_TOKEN }}

  apply:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "~> 1.5"
      - run: terraform init
        working-directory: catalog
        env:
          TF_VAR_cortex_api_token: ${{ secrets.CORTEX_API_TOKEN }}
      - run: terraform apply -auto-approve
        working-directory: catalog
        env:
          TF_VAR_cortex_api_token: ${{ secrets.CORTEX_API_TOKEN }}
```

Store `CORTEX_API_TOKEN` as a GitHub Actions secret. Now every PR shows a plan diff as a CI check, and every merge to main applies automatically.
````

- [ ] **Step 3: Verify the README appears in `cortex solutions list`**

```bash
poetry run cortex solutions list
```

Expected: a row showing "Terraform" with description "Manage your Cortex catalog as code using the Cortex Terraform provider."

- [ ] **Step 4: Commit**

```bash
git add cortexapps_cli/solutions/terraform/
git commit -m "feat: add terraform solution scaffold and README (CX-43)"
```

---

## Task 2: Terraform provider config files

**Files:**
- Create: `cortexapps_cli/solutions/terraform/_templates/terraform/provider.tf`
- Create: `cortexapps_cli/solutions/terraform/_templates/terraform/variables.tf`
- Create: `cortexapps_cli/solutions/terraform/_templates/terraform/terraform.tfvars.example`

**Interfaces:**
- Produces: three files consumed by `terraform init` and `terraform apply` in all subsequent tasks; `var.cortex_api_token` and `var.cortex_base_url` are referenced by all resource files

- [ ] **Step 1: Write provider.tf**

```hcl
terraform {
  required_providers {
    cortex = {
      source  = "cortexapps/cortex"
      version = "~> 0.6"
    }
  }
  required_version = ">= 1.5"
}

provider "cortex" {
  token        = var.cortex_api_token
  base_api_url = var.cortex_base_url
}
```

- [ ] **Step 2: Write variables.tf**

```hcl
variable "cortex_api_token" {
  description = "Cortex API token. Can also be set via the CORTEX_API_TOKEN environment variable."
  type        = string
  sensitive   = true
}

variable "cortex_base_url" {
  description = "Cortex API base URL."
  type        = string
  default     = "https://api.getcortexapp.com"
}
```

- [ ] **Step 3: Write terraform.tfvars.example**

```hcl
# Copy this file to terraform.tfvars and fill in your values.
# IMPORTANT: Never commit terraform.tfvars to source control — it contains your API token.
# Add terraform.tfvars to your .gitignore.

# Your Cortex API token.
# Alternatively, set the CORTEX_API_TOKEN environment variable and omit this line.
# cortex_api_token = "your-api-token-here"

# Cortex API base URL. Only change if you are on a self-hosted instance.
cortex_base_url = "https://api.getcortexapp.com"
```

- [ ] **Step 4: Verify files are present**

```bash
ls cortexapps_cli/solutions/terraform/_templates/terraform/
```

Expected output includes: `provider.tf  variables.tf  terraform.tfvars.example`

- [ ] **Step 5: Commit**

```bash
git add cortexapps_cli/solutions/terraform/_templates/terraform/
git commit -m "feat: add terraform provider config files (CX-43)"
```

---

## Task 3: teams.tf

**Files:**
- Create: `cortexapps_cli/solutions/terraform/_templates/terraform/teams.tf`

**Interfaces:**
- Produces: team tags `team-development`, `team-operations`, `team-security`, `team-qa` — referenced by `owners` blocks in ecommerce.tf and supply-chain.tf

- [ ] **Step 1: Write teams.tf**

```hcl
# teams.tf — Platform-owned
# Changes to teams (membership, new hires, reorgs) are made here via platform PR.

resource "cortex_catalog_entity" "team_development" {
  tag         = "team-development"
  name        = "Development"
  description = "Application development team responsible for Parts Unlimited's e-commerce platform and core services."

  groups = ["terraform-demo"]

  team = {
    members = [
      {
        name        = "Bill Palmer"
        email       = "bill.palmer@parts-unlimited.com"
        role        = "Team Lead"
        description = "IT Manager leading the Phoenix Project"
      },
      {
        name        = "Maxine Chambers"
        email       = "maxine.chambers@parts-unlimited.com"
        role        = "Senior Engineer"
        description = "Staff engineer on the Phoenix Project"
      },
      {
        name        = "Dev Magee"
        email       = "dev.magee@parts-unlimited.com"
        role        = "Engineer"
        description = "Developer on the Phoenix Project"
      }
    ]
  }
}

resource "cortex_catalog_entity" "team_operations" {
  tag         = "team-operations"
  name        = "IT Operations"
  description = "Infrastructure, reliability, and operations for Parts Unlimited's production systems."

  groups = ["terraform-demo"]

  team = {
    members = [
      {
        name        = "Brent Geller"
        email       = "brent.geller@parts-unlimited.com"
        role        = "Principal Engineer"
        description = "Indispensable operations expert and bottleneck"
      },
      {
        name        = "Wes Davis"
        email       = "wes.davis@parts-unlimited.com"
        role        = "Operations Manager"
        description = "Manages day-to-day operations work"
      }
    ]
  }
}

resource "cortex_catalog_entity" "team_security" {
  tag         = "team-security"
  name        = "Information Security"
  description = "Security, compliance, and risk management for Parts Unlimited."

  groups = ["terraform-demo"]

  team = {
    members = [
      {
        name        = "John Pesche"
        email       = "john.pesche@parts-unlimited.com"
        role        = "CISO"
        description = "Chief Information Security Officer"
      }
    ]
  }
}

resource "cortex_catalog_entity" "team_qa" {
  tag         = "team-qa"
  name        = "Quality Assurance"
  description = "Testing, QA, and release verification for Parts Unlimited services."

  groups = ["terraform-demo"]

  team = {
    members = [
      {
        name        = "Patty McKee"
        email       = "patty.mckee@parts-unlimited.com"
        role        = "QA Manager"
        description = "Manages QA processes and testing"
      }
    ]
  }
}
```

> **Note on `team` block syntax:** The exact nested HCL for team members may differ from what's shown. Verify against the provider docs at https://registry.terraform.io/providers/cortexapps/cortex/latest/docs/resources/catalog_entity — look for `team` and `members` attributes. If `team { members [...] }` doesn't work, the provider may use a flat `members` block at the resource level. Run `terraform validate` after writing and fix any schema errors.

- [ ] **Step 2: Commit**

```bash
git add cortexapps_cli/solutions/terraform/_templates/terraform/teams.tf
git commit -m "feat: add teams.tf for terraform solution (CX-43)"
```

---

## Task 4: ecommerce.tf (initial Bronze state)

**Files:**
- Create: `cortexapps_cli/solutions/terraform/_templates/terraform/ecommerce.tf`

**Interfaces:**
- Produces: entity tags `domain-ecommerce`, `phoenix`, `parts-catalog-api`, `payments-service`
- Consumes: team tag `team-development` (from Task 3)

- [ ] **Step 1: Write ecommerce.tf**

```hcl
# ecommerce.tf — E-Commerce team-owned
# This file defines the E-Commerce domain and all services within it.
# The e-commerce team submits PRs to this file to add/update services.
#
# NOTE: Services are intentionally at Bronze level only (no links, no metadata).
# See _templates/terraform-delta/ecommerce.tf for the Silver-state version.

resource "cortex_catalog_entity" "domain_ecommerce" {
  tag         = "domain-ecommerce"
  name        = "E-Commerce"
  description = "Customer-facing e-commerce platform including product catalog, checkout, and payments."
  type        = "domain"

  groups = ["terraform-demo"]
}

resource "cortex_catalog_entity" "phoenix" {
  tag         = "phoenix"
  name        = "The Phoenix Project"
  description = "Main e-commerce monolith handling browsing and checkout."

  owners = [
    {
      name     = "team-development"
      type     = "group"
      provider = "CORTEX"
    }
  ]

  groups = ["terraform-demo", "domain:ecommerce"]

  git = {
    github = {
      repository = "parts-unlimited/phoenix"
      base_path  = "/"
    }
  }
}

resource "cortex_catalog_entity" "parts_catalog_api" {
  tag         = "parts-catalog-api"
  name        = "Parts Catalog API"
  description = "REST API for browsing the parts catalog."

  owners = [
    {
      name     = "team-development"
      type     = "group"
      provider = "CORTEX"
    }
  ]

  groups = ["terraform-demo", "domain:ecommerce"]

  git = {
    github = {
      repository = "parts-unlimited/parts-catalog-api"
      base_path  = "/"
    }
  }
}

resource "cortex_catalog_entity" "payments_service" {
  tag         = "payments-service"
  name        = "Payments Service"
  description = "Payment processing and refund handling."

  owners = [
    {
      name     = "team-development"
      type     = "group"
      provider = "CORTEX"
    }
  ]

  groups = ["terraform-demo", "domain:ecommerce"]

  git = {
    github = {
      repository = "parts-unlimited/payments-service"
      base_path  = "/"
    }
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add cortexapps_cli/solutions/terraform/_templates/terraform/ecommerce.tf
git commit -m "feat: add ecommerce.tf for terraform solution (CX-43)"
```

---

## Task 5: supply-chain.tf (initial Bronze state)

**Files:**
- Create: `cortexapps_cli/solutions/terraform/_templates/terraform/supply-chain.tf`

**Interfaces:**
- Produces: entity tags `domain-supply-chain`, `inventory-service`, `ordering-service`, `shipping-service`
- Consumes: team tag `team-operations` (from Task 3)

- [ ] **Step 1: Write supply-chain.tf**

```hcl
# supply-chain.tf — Supply Chain team-owned
# This file defines the Supply Chain domain and all services within it.
# The supply chain team submits PRs to this file to add/update services.

resource "cortex_catalog_entity" "domain_supply_chain" {
  tag         = "domain-supply-chain"
  name        = "Supply Chain"
  description = "Inventory, ordering, and shipping services supporting Parts Unlimited's fulfillment operations."
  type        = "domain"

  groups = ["terraform-demo"]
}

resource "cortex_catalog_entity" "inventory_service" {
  tag         = "inventory-service"
  name        = "Inventory Service"
  description = "Real-time inventory tracking across all Parts Unlimited warehouses."

  owners = [
    {
      name     = "team-operations"
      type     = "group"
      provider = "CORTEX"
    }
  ]

  groups = ["terraform-demo", "domain:supply-chain"]

  git = {
    github = {
      repository = "parts-unlimited/inventory-service"
      base_path  = "/"
    }
  }
}

resource "cortex_catalog_entity" "ordering_service" {
  tag         = "ordering-service"
  name        = "Ordering Service"
  description = "Order placement, validation, and fulfillment coordination."

  owners = [
    {
      name     = "team-development"
      type     = "group"
      provider = "CORTEX"
    }
  ]

  groups = ["terraform-demo", "domain:supply-chain"]

  git = {
    github = {
      repository = "parts-unlimited/ordering-service"
      base_path  = "/"
    }
  }
}

resource "cortex_catalog_entity" "shipping_service" {
  tag         = "shipping-service"
  name        = "Shipping Service"
  description = "Shipping and logistics tracking for Parts Unlimited orders."

  owners = [
    {
      name     = "team-operations"
      type     = "group"
      provider = "CORTEX"
    }
  ]

  groups = ["terraform-demo", "domain:supply-chain"]

  git = {
    github = {
      repository = "parts-unlimited/shipping-service"
      base_path  = "/"
    }
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add cortexapps_cli/solutions/terraform/_templates/terraform/supply-chain.tf
git commit -m "feat: add supply-chain.tf for terraform solution (CX-43)"
```

---

## Task 6: scorecards.tf

**Files:**
- Create: `cortexapps_cli/solutions/terraform/_templates/terraform/scorecards.tf`

**Interfaces:**
- Produces: scorecard tag `production-readiness`; Bronze rules pass for all initial services; Silver rules intentionally fail until delta is applied

- [ ] **Step 1: Write scorecards.tf**

The scorecard uses only Terraform-native rules — no external integrations (no PagerDuty, no OpsGenie) required. Services start at Bronze and the delta moves `phoenix` to Silver.

```hcl
# scorecards.tf — Platform-owned
# Defines the Production Readiness scorecard.
# Bronze: automatically achieved by all properly-defined services.
# Silver: requires adding links and metadata — see the delta.
# Gold: requires shared ownership and a rich description — aspirational.

resource "cortex_scorecard" "production_readiness" {
  tag         = "production-readiness"
  name        = "Production Readiness"
  description = "Measures how production-ready a Parts Unlimited service is. Bronze is table stakes; Gold is the aspirational standard."
  draft       = false

  ladder = {
    levels = [
      {
        name  = "Gold"
        rank  = 3
        color = "#D7AC58"
      },
      {
        name  = "Silver"
        rank  = 2
        color = "#C0C0C0"
      },
      {
        name  = "Bronze"
        rank  = 1
        color = "#CD7F32"
      }
    ]
  }

  rules = [
    # ── Bronze ────────────────────────────────────────────────────────────────
    {
      title       = "Has description"
      description = "Service must have a non-empty description."
      expression  = "entity.description().length > 0"
      weight      = 1
      level       = "Bronze"
    },
    {
      title       = "Has owner team"
      description = "Service must be owned by at least one team."
      expression  = "owners.teams.size() > 0"
      weight      = 1
      level       = "Bronze"
    },
    {
      title       = "Has git configured"
      description = "Service must have a git repository linked."
      expression  = "git != null"
      weight      = 1
      level       = "Bronze"
    },

    # ── Silver ────────────────────────────────────────────────────────────────
    {
      title       = "Has at least one link"
      description = "Service must have at least one link (runbook, docs, dashboard, etc.)."
      expression  = "links.size() > 0"
      weight      = 1
      level       = "Silver"
    },
    {
      title       = "Has terraform-workspace metadata"
      description = "Service must declare its Terraform workspace via the terraform-workspace metadata key."
      expression  = "customData.exists(d, d.key == \"terraform-workspace\")"
      weight      = 1
      level       = "Silver"
    },
    {
      title       = "Meaningful description"
      description = "Service description should be at least 30 characters."
      expression  = "entity.description().length >= 30"
      weight      = 1
      level       = "Silver"
    },

    # ── Gold ──────────────────────────────────────────────────────────────────
    {
      title       = "Rich description"
      description = "Service description should be at least 50 characters."
      expression  = "entity.description().length >= 50"
      weight      = 1
      level       = "Gold"
    },
    {
      title       = "Shared ownership"
      description = "Critical services should be owned by at least two teams to avoid single points of knowledge."
      expression  = "owners.teams.size() >= 2"
      weight      = 1
      level       = "Gold"
    },
    {
      title       = "Has runbook"
      description = "Service must have a runbook link for on-call responders."
      expression  = "links.exists(l, l.type == \"runbook\")"
      weight      = 1
      level       = "Gold"
    }
  ]

  filter = {
    types = {
      include = ["service"]
    }
  }

  evaluation = {
    window = 24
  }
}
```

> **Note on Cortex expression language:** `owners.teams.size()` and `customData.exists(...)` are Cortex Expression Language (CEL-like). Verify these expressions work against your Cortex instance by checking the scorecard after `terraform apply`. If a Bronze rule shows as failing for a service that clearly has an owner, the expression path may need adjusting — check Cortex scorecard rule documentation for the correct field names.

- [ ] **Step 2: Commit**

```bash
git add cortexapps_cli/solutions/terraform/_templates/terraform/scorecards.tf
git commit -m "feat: add scorecards.tf for terraform solution (CX-43)"
```

---

## Task 7: terraform-delta files

**Files:**
- Create: `cortexapps_cli/solutions/terraform/_templates/terraform-delta/ecommerce.tf`
- Create: `cortexapps_cli/solutions/terraform/_templates/terraform-delta/teams.tf`

**Interfaces:**
- Produces: drop-in replacement files for `_templates/terraform/ecommerce.tf` and `teams.tf`; when copied into a working directory and applied, `phoenix` gains Silver, `notification-service` is created, Sarah Connor joins `team-development`
- Consumes: same entity tags and owner references as Tasks 3 and 4 — these files must be self-contained complete replacements (all original resources present + changes)

- [ ] **Step 1: Write terraform-delta/ecommerce.tf**

This is a complete replacement for `ecommerce.tf`. It includes all original resources unchanged, plus: `phoenix` gets links + metadata (Bronze → Silver), `notification-service` is added.

```hcl
# terraform-delta/ecommerce.tf
# ─────────────────────────────────────────────────────────────────────────────
# DELTA VERSION — copy over ecommerce.tf and run `terraform plan` to see diff.
#
# Changes from baseline:
#   phoenix           → promoted to Silver (links + metadata added, description expanded)
#   notification-service → NEW service (+ create in plan output)
#
# Unchanged: domain-ecommerce, parts-catalog-api, payments-service
# ─────────────────────────────────────────────────────────────────────────────

resource "cortex_catalog_entity" "domain_ecommerce" {
  tag         = "domain-ecommerce"
  name        = "E-Commerce"
  description = "Customer-facing e-commerce platform including product catalog, checkout, and payments."
  type        = "domain"

  groups = ["terraform-demo"]
}

# CHANGED: description expanded (≥ 30 chars for Silver rule 3),
#          links added (Silver rule 1), metadata added (Silver rule 2)
resource "cortex_catalog_entity" "phoenix" {
  tag         = "phoenix"
  name        = "The Phoenix Project"
  description = "Main e-commerce monolith for Parts Unlimited, handling product browsing, cart, and checkout flows."

  owners = [
    {
      name     = "team-development"
      type     = "group"
      provider = "CORTEX"
    }
  ]

  groups = ["terraform-demo", "domain:ecommerce"]

  git = {
    github = {
      repository = "parts-unlimited/phoenix"
      base_path  = "/"
    }
  }

  links = [
    {
      name = "Runbook"
      type = "runbook"
      url  = "https://wiki.parts-unlimited.com/runbooks/phoenix"
    },
    {
      name = "Architecture Docs"
      type = "documentation"
      url  = "https://wiki.parts-unlimited.com/architecture/phoenix"
    }
  ]

  metadata = jsonencode({
    "terraform-workspace" = "phoenix-prod"
  })
}

resource "cortex_catalog_entity" "parts_catalog_api" {
  tag         = "parts-catalog-api"
  name        = "Parts Catalog API"
  description = "REST API for browsing the parts catalog."

  owners = [
    {
      name     = "team-development"
      type     = "group"
      provider = "CORTEX"
    }
  ]

  groups = ["terraform-demo", "domain:ecommerce"]

  git = {
    github = {
      repository = "parts-unlimited/parts-catalog-api"
      base_path  = "/"
    }
  }
}

resource "cortex_catalog_entity" "payments_service" {
  tag         = "payments-service"
  name        = "Payments Service"
  description = "Payment processing and refund handling."

  owners = [
    {
      name     = "team-development"
      type     = "group"
      provider = "CORTEX"
    }
  ]

  groups = ["terraform-demo", "domain:ecommerce"]

  git = {
    github = {
      repository = "parts-unlimited/payments-service"
      base_path  = "/"
    }
  }
}

# NEW SERVICE — will show as `+ create` in terraform plan
resource "cortex_catalog_entity" "notification_service" {
  tag         = "notification-service"
  name        = "Notification Service"
  description = "Handles email, SMS, and push notifications for Parts Unlimited customer events."

  owners = [
    {
      name     = "team-development"
      type     = "group"
      provider = "CORTEX"
    }
  ]

  groups = ["terraform-demo", "domain:ecommerce"]

  git = {
    github = {
      repository = "parts-unlimited/notification-service"
      base_path  = "/"
    }
  }
}
```

- [ ] **Step 2: Write terraform-delta/teams.tf**

Complete replacement for `teams.tf`. All original teams unchanged; Sarah Connor added to `team-development`.

```hcl
# terraform-delta/teams.tf
# ─────────────────────────────────────────────────────────────────────────────
# DELTA VERSION — copy over teams.tf and run `terraform plan` to see diff.
#
# Changes from baseline:
#   team-development → Sarah Connor added (~ update in plan output)
#
# Unchanged: team-operations, team-security, team-qa
# ─────────────────────────────────────────────────────────────────────────────

# CHANGED: Sarah Connor added
resource "cortex_catalog_entity" "team_development" {
  tag         = "team-development"
  name        = "Development"
  description = "Application development team responsible for Parts Unlimited's e-commerce platform and core services."

  groups = ["terraform-demo"]

  team = {
    members = [
      {
        name        = "Bill Palmer"
        email       = "bill.palmer@parts-unlimited.com"
        role        = "Team Lead"
        description = "IT Manager leading the Phoenix Project"
      },
      {
        name        = "Maxine Chambers"
        email       = "maxine.chambers@parts-unlimited.com"
        role        = "Senior Engineer"
        description = "Staff engineer on the Phoenix Project"
      },
      {
        name        = "Dev Magee"
        email       = "dev.magee@parts-unlimited.com"
        role        = "Engineer"
        description = "Developer on the Phoenix Project"
      },
      {
        name        = "Sarah Connor"
        email       = "sarah.connor@parts-unlimited.com"
        role        = "Engineer"
        description = "New hire joining the Phoenix Project team"
      }
    ]
  }
}

resource "cortex_catalog_entity" "team_operations" {
  tag         = "team-operations"
  name        = "IT Operations"
  description = "Infrastructure, reliability, and operations for Parts Unlimited's production systems."

  groups = ["terraform-demo"]

  team = {
    members = [
      {
        name        = "Brent Geller"
        email       = "brent.geller@parts-unlimited.com"
        role        = "Principal Engineer"
        description = "Indispensable operations expert and bottleneck"
      },
      {
        name        = "Wes Davis"
        email       = "wes.davis@parts-unlimited.com"
        role        = "Operations Manager"
        description = "Manages day-to-day operations work"
      }
    ]
  }
}

resource "cortex_catalog_entity" "team_security" {
  tag         = "team-security"
  name        = "Information Security"
  description = "Security, compliance, and risk management for Parts Unlimited."

  groups = ["terraform-demo"]

  team = {
    members = [
      {
        name        = "John Pesche"
        email       = "john.pesche@parts-unlimited.com"
        role        = "CISO"
        description = "Chief Information Security Officer"
      }
    ]
  }
}

resource "cortex_catalog_entity" "team_qa" {
  tag         = "team-qa"
  name        = "Quality Assurance"
  description = "Testing, QA, and release verification for Parts Unlimited services."

  groups = ["terraform-demo"]

  team = {
    members = [
      {
        name        = "Patty McKee"
        email       = "patty.mckee@parts-unlimited.com"
        role        = "QA Manager"
        description = "Manages QA processes and testing"
      }
    ]
  }
}
```

- [ ] **Step 3: Commit**

```bash
git add cortexapps_cli/solutions/terraform/_templates/terraform-delta/
git commit -m "feat: add terraform-delta files for terraform solution (CX-43)"
```

---

## Task 8: setup.py

**Files:**
- Create: `cortexapps_cli/solutions/terraform/setup.py`

**Interfaces:**
- Consumes: `kwargs["cortex_api_key"]`, `kwargs["cortex_base_url"]` from CLI session; `_templates/terraform/` directory (Tasks 2–6); `SolutionSetup` from `cortexapps_cli.solutions._lib.setup_base`
- Produces: entry point `main(**kwargs)` invoked by `cortex solutions post-install -s terraform`; working directory at user-specified path with all `.tf` files and `terraform.tfvars`; entities created in Cortex via `terraform apply`

- [ ] **Step 1: Write setup.py**

```python
"""
Post-install setup for the terraform solution.
Verifies Terraform is installed, copies template files to a working directory,
writes credentials, and runs terraform init + apply.

Run via: cortex solutions post-install -s terraform
"""

SETUP_DESCRIPTION = (
    "Sets up the Parts Unlimited demo org in your Cortex instance using the "
    "Cortex Terraform provider. Requires Terraform >= 1.5 — install at "
    "https://developer.hashicorp.com/terraform/install"
)

import shutil
import subprocess
import sys
from pathlib import Path

try:
    from cortexapps_cli.solutions._lib.setup_base import SolutionSetup
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from _lib.setup_base import SolutionSetup

_TEMPLATES_DIR = Path(__file__).parent / "_templates" / "terraform"
_DELTA_DIR = Path(__file__).parent / "_templates" / "terraform-delta"

_GITIGNORE_ENTRIES = [
    "terraform.tfvars",
    ".terraform/",
    "*.tfstate",
    "*.tfstate.backup",
    ".terraform.lock.hcl",
]


class TerraformSetup(SolutionSetup):
    solution_tag = "terraform"

    def collect_prompts(self) -> None:
        self.prompt(
            "work_dir",
            "Working directory for Terraform files",
            default=str(Path.home() / "parts-unlimited-terraform"),
            env_var="TERRAFORM_WORK_DIR",
        )

    def steps(self) -> list[tuple[str, callable]]:
        return [
            ("Check Terraform CLI", self._check_terraform),
            ("Create working directory", self._create_work_dir),
            ("Copy Terraform files", self._copy_files),
            ("Write terraform.tfvars", self._write_tfvars),
            ("Write .gitignore", self._write_gitignore),
            ("terraform init", self._terraform_init),
            ("terraform apply", self._terraform_apply),
        ]

    def post_steps(self) -> None:
        work_dir = self._answers["work_dir"]
        delta_dir = _DELTA_DIR

        print("\n✓ Parts Unlimited demo org created in Cortex via Terraform!\n")
        print(f"  Terraform files are at: {work_dir}\n")
        print("─" * 60)
        print("NEXT: Try the delta to see Terraform's incremental update\n")
        print("  1. Copy the delta files into your working directory:")
        print(f"     cp {delta_dir}/ecommerce.tf {work_dir}/ecommerce.tf")
        print(f"     cp {delta_dir}/teams.tf {work_dir}/teams.tf\n")
        print("  2. Preview the changes:")
        print(f"     cd {work_dir} && terraform plan\n")
        print("     Look for:")
        print("       ~ cortex_catalog_entity.phoenix       (update: links + metadata added)")
        print("       + cortex_catalog_entity.notification_service  (create: new service)")
        print("       ~ cortex_catalog_entity.team_development      (update: new member)\n")
        print("  3. Apply:")
        print(f"     terraform apply\n")
        print("  4. Check the Production Readiness scorecard in Cortex.")
        print("     The Phoenix Project should now show Silver.\n")
        print("─" * 60)
        print("To use Terraform for your real catalog, see the CI/CD integration")
        print("section in: cortex solutions info -s terraform")

    # ── Private step implementations ──────────────────────────────────────────

    def _check_terraform(self) -> None:
        if self.already_done("check_terraform"):
            return
        result = shutil.which("terraform")
        if result is None:
            print(
                "\nERROR: terraform CLI not found in PATH.\n"
                "Install Terraform >= 1.5 from: https://developer.hashicorp.com/terraform/install",
                file=sys.stderr,
            )
            raise RuntimeError("terraform not found")
        # Check version >= 1.5
        try:
            out = subprocess.check_output(
                ["terraform", "version", "-json"], text=True
            )
            import json
            version_str = json.loads(out).get("terraform_version", "0.0.0")
            major, minor, *_ = (int(x) for x in version_str.split("."))
            if (major, minor) < (1, 5):
                raise RuntimeError(
                    f"Terraform {version_str} is too old. Version >= 1.5 required.\n"
                    "Upgrade at: https://developer.hashicorp.com/terraform/install"
                )
        except (subprocess.CalledProcessError, KeyError, ValueError):
            # If version check fails, proceed — let terraform itself error if needed
            pass
        self.mark_done("check_terraform")

    def _create_work_dir(self) -> None:
        if self.already_done("create_work_dir"):
            return
        work_dir = Path(self._answers["work_dir"]).expanduser()
        work_dir.mkdir(parents=True, exist_ok=True)
        self.mark_done("create_work_dir")

    def _copy_files(self) -> None:
        if self.already_done("copy_files"):
            return
        work_dir = Path(self._answers["work_dir"]).expanduser()
        for src in _TEMPLATES_DIR.iterdir():
            if src.is_file():
                shutil.copy2(src, work_dir / src.name)
        self.mark_done("copy_files")

    def _write_tfvars(self) -> None:
        if self.already_done("write_tfvars"):
            return
        work_dir = Path(self._answers["work_dir"]).expanduser()
        api_key = self._kwargs.get("cortex_api_key", "")
        base_url = self._kwargs.get("cortex_base_url", "https://api.getcortexapp.com")
        tfvars = work_dir / "terraform.tfvars"
        tfvars.write_text(
            f'cortex_api_token = "{api_key}"\n'
            f'cortex_base_url  = "{base_url}"\n'
        )
        self.mark_done("write_tfvars")

    def _write_gitignore(self) -> None:
        if self.already_done("write_gitignore"):
            return
        work_dir = Path(self._answers["work_dir"]).expanduser()
        gitignore = work_dir / ".gitignore"
        existing = gitignore.read_text() if gitignore.exists() else ""
        additions = [e for e in _GITIGNORE_ENTRIES if e not in existing]
        if additions:
            with gitignore.open("a") as f:
                if existing and not existing.endswith("\n"):
                    f.write("\n")
                f.write("\n".join(additions) + "\n")
        self.mark_done("write_gitignore")

    def _terraform_init(self) -> None:
        if self.already_done("terraform_init"):
            return
        work_dir = Path(self._answers["work_dir"]).expanduser()
        result = subprocess.run(
            ["terraform", "init"],
            cwd=work_dir,
            capture_output=False,  # stream output to terminal
        )
        if result.returncode != 0:
            raise RuntimeError("terraform init failed — see output above")
        self.mark_done("terraform_init")

    def _terraform_apply(self) -> None:
        if self.already_done("terraform_apply"):
            return
        work_dir = Path(self._answers["work_dir"]).expanduser()
        result = subprocess.run(
            ["terraform", "apply", "-auto-approve"],
            cwd=work_dir,
            capture_output=False,  # stream output to terminal
        )
        if result.returncode != 0:
            raise RuntimeError(
                "terraform apply failed — see output above.\n"
                f"State may be partially created. Retry from: {work_dir}"
            )
        self.mark_done("terraform_apply")


def main(**kwargs):
    TerraformSetup(**kwargs).run()
```

> **Note on `self._answers` and `self._kwargs`:** Check `setup_base.py` to confirm the attribute names for stored prompt answers and kwargs. From reading `github-actions-deploy/setup.py`, answers are accessed via `self._answers["key"]` and kwargs via `self._kwargs`. If the base class uses different names, adjust accordingly.

- [ ] **Step 2: Verify the module is importable**

```bash
poetry run python -c "from cortexapps_cli.solutions.terraform.setup import main; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add cortexapps_cli/solutions/terraform/setup.py
git commit -m "feat: add setup.py for terraform solution (CX-43)"
```

---

## Task 9: End-to-end test

**Files:** None created — this is a manual verification task.

- [ ] **Step 1: Verify solution appears in list and info**

```bash
poetry run cortex solutions list
poetry run cortex solutions info -s terraform
```

Expected: `list` shows Terraform row; `info` shows full README content.

- [ ] **Step 2: Verify terraform template files are syntactically valid**

If you have Terraform installed locally:

```bash
cd /tmp && mkdir tf-validate && cp cortexapps_cli/solutions/terraform/_templates/terraform/*.tf tf-validate/
# Create a minimal tfvars so validate doesn't error on missing required vars
echo 'cortex_api_token = "fake"' > tf-validate/terraform.tfvars
cd tf-validate && terraform init && terraform validate
```

Expected: `Success! The configuration is valid.`

If `terraform validate` reports schema errors (unknown attribute, incorrect type, etc.):
1. Open https://registry.terraform.io/providers/cortexapps/cortex/latest/docs/resources/catalog_entity in a browser
2. Find the correct attribute name
3. Update the affected `.tf` files in both `_templates/terraform/` and `_templates/terraform-delta/`

- [ ] **Step 3: Run the full post-install against a real Cortex instance**

Requires `CORTEX_API_KEY` to be set.

```bash
poetry run cortex solutions post-install -s terraform
```

Accept the default working directory. Watch `terraform init` download the provider and `terraform apply` create entities.

- [ ] **Step 4: Verify entities in Cortex**

In the Cortex UI, filter catalog by group `terraform-demo`. You should see:
- 4 teams
- 2 domains
- 6 services
- All 6 services at Bronze on Production Readiness scorecard

- [ ] **Step 5: Apply the delta**

```bash
cp cortexapps_cli/solutions/terraform/_templates/terraform-delta/ecommerce.tf ~/parts-unlimited-terraform/ecommerce.tf
cp cortexapps_cli/solutions/terraform/_templates/terraform-delta/teams.tf ~/parts-unlimited-terraform/teams.tf
cd ~/parts-unlimited-terraform && terraform plan
```

Confirm plan output shows:
- `~ cortex_catalog_entity.phoenix` (update)
- `+ cortex_catalog_entity.notification_service` (create)
- `~ cortex_catalog_entity.team_development` (update)

Then apply:

```bash
terraform apply
```

- [ ] **Step 6: Verify scorecard promotion**

Open Production Readiness scorecard in Cortex. The Phoenix Project should now show **Silver**.

- [ ] **Step 7: Final commit if any fixes were needed**

```bash
git add -p  # stage only intentional changes
git commit -m "fix: correct terraform HCL field names after validation (CX-43)"
```
