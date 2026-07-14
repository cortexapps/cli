---
name: Environments, Releases & Clusters
description: Model your deployment hierarchy from clusters to service versions, with CVE vulnerability exposure.
---

# Environments, Releases & Clusters

Model your deployment hierarchy — from clusters down to service versions — and surface CVE vulnerability exposure across environments.

## Overview

```
┌─────────────────────────────────────────────────────────┐
│                     ENVIRONMENT                         │
│               gcp-prod-us-east-1                        │
│   cloudType:gcp  │  envType:prod  │  region:us-east-1   │
└─────────────────────────┬───────────────────────────────┘
                          │ environments
                          ▼
              ┌───────────────────────┐
              │        RELEASE        │
              │  release-2026-07-01   │
              └───────────┬───────────┘
                          │ environments
              ┌───────────┴───────────┐
              ▼                       ▼
   ┌────────────────────┐  ┌────────────────────┐
   │  SERVICE VERSION   │  │  SERVICE VERSION   │
   │   payments-1.6.1   │  │    auth-2.1.0      │
   │  ⚠ CVE-2024-3195  │  │  packages: clean   │
   │  python-requests   │  │  flask, pyjwt      │
   │     2.32.1         │  │                    │
   └────────────────────┘  └────────────────────┘
            │
            │ custom-data.service
            ▼
   ┌────────────────────┐
   │      SERVICE       │
   │      payments      │
   └────────────────────┘
```

Query: *"Which environments are affected by CVE-2024-3195?"*
→ service-version with CVE → release → environment: `gcp-prod-us-east-1`, `gcp-staging-us-east-1`

## What's Included

**Entity types:** `environment`, `release`, `service-version`

**Relationship type:** `environments` — one type powers a single catalog view of the full hierarchy (environment → release → service-version)

**Sample entities:**
- 3 environments: `gcp-prod-us-east-1`, `gcp-staging-us-east-1`, `aws-dev-us-west-2`
- 6 releases (2 per environment)
- 14 service versions across 4 services (`payments`, `auth`, `api-gateway`, `notifications`)
- Demo CVE: `cve-2024-3195` in `payments-1.6.1` — exposed in prod and staging

**Scorecard:** Am I Vulnerable? — surfaces CVE exposure per environment

**Workflows:**
- `create-environment.yaml` — Cortex workflow: prompts for cloudType/envType/region, creates environment entity
- `create-release.yaml` — Cortex workflow: creates release entity linked to an environment
- `trigger-github-release.yaml` — Cortex workflow: triggers a GitHub release for a service
- `.github/workflows/cortex-service-version.yaml` — GitHub Actions: creates service-version entity on release publish

## Installation

```
cortex solutions install -s environments
```

To overwrite existing resources:

```
cortex solutions install -s environments --force
```

## After Installing

1. Go to **Catalogs** in the Cortex UI
2. Click **New Catalog**
3. Select relationship type: **environments**
4. Set root entity type: **environment**
5. Name it **Environments**

> **Coming soon:** Catalog creation will be automated once catalog API support is added to the CLI.

## How the process works

```
1. Create Environment
   Cortex Workflow: create-environment
   └── Prompts: cloudType, envType, region
   └── Creates environment entity (e.g. gcp-prod-us-east-1) with groups
   └── [Add your] cluster provisioning logic here

2. Create a Release
   Cortex Workflow: create-release
   └── Creates release entity linked to environment via `environments` relationship
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
       └── "Am I Vulnerable?" scorecard evaluates per environment

5. Query with MCP
   └── "Which environments are affected by cve-2024-3195?"
   └── "What version of payments is in prod?"
```

## MCP Query Examples

- *"Which environments are affected by cve-2024-3195?"*
- *"What version of payments is running in gcp-prod-us-east-1?"*
- *"List all HIGH CVEs across service versions in the prod environment"*
- *"Which environments have payments-1.6.1 deployed?"*
