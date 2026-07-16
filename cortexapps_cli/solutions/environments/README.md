---
name: Environments, Releases & Clusters
description: Model your deployment hierarchy from clusters to service versions, with CVE vulnerability exposure.
---

# Environments, Releases & Clusters

Model your deployment hierarchy — from clusters down to service versions — and surface CVE vulnerability exposure across environments.

## Overview

```
┌─────────────────────────────────────────────────────────┐
│                     environment                         │
│               gcp-prod-us-east-1                        │
│   cloudType:gcp  |  envType:prod  |  region:us-east-1   │
└─────────────────────────┬───────────────────────────────┘
                          │ environments
                          ▼
              ┌───────────────────────┐    ┌──────────────────┐
              │        release        │    │     service      │
              │  release-2026-07-01   │    │     payments     │
              └───────────┬───────────┘    └────────┬─────────┘
                          │ environments            │ versions
                          └────────────┬────────────┘
                                       ▼
                           ┌───────────────────────┐
                           │    service-version    │
                           │    payments-1.6.1     │
                           └───────────────────────┘
```

Once service-versions carry package and CVE metadata (via Snyk/Wiz), MCP can answer:
*"Which environments are affected by CVE-2024-3195?"*
→ service-version with CVE → release → environment: `gcp-prod-us-east-1`, `gcp-prod-us-west-1`

## What's Included

**Entity types:** `environment`, `release`, `service-version`

**Relationship types:**
- `environments` — powers the deployment catalog view (environment → release → service-version)
- `versions` — connects each service to its versioned artifacts (service → service-version)

**Sample entities:**
- 4 environments: `gcp-prod-us-east-1`, `gcp-prod-us-west-1`, `gcp-staging-us-east-1`, `aws-dev-us-west-2`
- 4 releases (1 per environment)
- 10 services: `payments`, `auth`, `api-gateway`, `notifications`, `user-service`, `order-service`, `billing`, `search`, `cart`, `checkout`
- 30 service-versions (2–3 per service)
- Demo CVE: `cve-2024-3195` in `payments-1.6.1` — exposed in both prod environments
- `auth-2.1.0` deployed in prod-east, prod-west, and staging (stable, rarely changes)
- `cart-1.0.2` deployed in all 4 environments (extremely stable)
- `checkout` has different versions per environment (active development + staggered rollout)

**Workflows:**
- `create-environment.yaml` — Cortex workflow: prompts for cloudType/envType/region, creates environment entity
- `create-release.yaml` — Cortex workflow: entity picker for service-versions, creates release entity with relationships
- `trigger-github-release.yaml` — Cortex workflow: triggers a GitHub release for a service

## Installation

```
cortex solutions install -s environments
```

## After Installing

**Set up your Environments catalog**

Create a catalog to visualize the deployment hierarchy:

1. Go to [Catalogs](https://app.getcortexapp.com/admin/catalog) → **New Catalog**
2. Relationship type: `environments`
3. Root entity type: `environment`
4. Name it **Environments**

> Catalog creation will be automated once catalog API support is added to the CLI.

**Try the workflows**

Three workflows were installed. Go to [Workflows](https://app.getcortexapp.com/admin/workflows) in the Cortex UI:

- **Create Environment** (`create-environment`) — provision a new environment entity
- **Create Release** (`create-release`) — create a release linked to service versions
- **Trigger GitHub Release** (`trigger-github-release`) — publish a service version via GitHub Actions

These are all stub workflows. You might add the creation of these entities as part of your automated CI/CD process. You might extend these workflows and call them via the Cortex API. These are included to show conceptually what you'll want to create/maintain.

## How the process works

```
1. Create Environment
   Cortex Workflow: create-environment
   └── Prompts: cloudType, envType, region
   └── Creates environment entity (e.g. gcp-prod-us-east-1) with groups
   └── [Add your] cluster provisioning logic here

2. Create a Release
   Cortex Workflow: create-release
   └── Entity picker selects service versions to include
   └── Creates release entity with environments relationships to each version
   └── [Add your] deployment orchestration here

3. Publish Service Versions
   Cortex Workflow: trigger-github-release
   └── Triggers GitHub release on service repo
       └── GitHub Actions: cortex-service-version.yaml fires
           └── Creates service-version entity with package/CVE metadata
           └── Links to release via `environments` relationship

4. Vulnerability Data
   Your Snyk/Wiz pipeline
   └── Pushes CVE data to service-version custom metadata
   └── Pushes aggregated counts to environment custom metrics

5. Query with MCP
   └── "Which environments are affected by cve-2024-3195?"
   └── "What version of payments is in prod?"
```

## MCP Query Examples

- *"Which environments are affected by cve-2024-3195?"*
- *"What version of payments is running in gcp-prod-us-east-1?"*
- *"List all service versions deployed in the prod environments"*
- *"Which environments have payments-1.6.1 deployed?"*
- *"What is the difference between gcp-prod-us-east-1 and gcp-prod-us-west-1?"*

## Caveats

- **MCP queries are multi-hop.** The deployment hierarchy (environment → release → service-version) requires multiple API calls to traverse. For large catalogs with many environments, releases, and service-versions, these queries can be slow. This solution works best as a pure catalog/browsing solution with MCP for ad-hoc queries.

- **CQL cannot traverse related entity metadata.** CQL rules can traverse relationship chains (e.g. `entity.destinations(relationshipType = "environments", depth = 2)`) and filter by entity type or tag, but cannot access custom metadata on related entities. A scorecard rule like "does any deployed service-version have a HIGH CVE?" is not expressible in CQL today without modeling vulnerabilities as first-class entities linked via a dedicated relationship type.
