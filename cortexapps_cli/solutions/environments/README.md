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

Legend
┌──────────────────────────────────┐
│  x-cortex-type                   │
│  x-cortex-tag → workspace link   │
└─────────────────┬────────────────┘
                  │ relationship-tag
                  ▼
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

1. Go to [Catalogs](https://app.getcortexapp.com/admin/catalogs) → **New Catalog**
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
