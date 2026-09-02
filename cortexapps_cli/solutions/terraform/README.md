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
