---
name: Environments, Releases & Clusters
description: Model your deployment hierarchy from clusters to service versions, with CVE vulnerability exposure.
---

# Environments, Releases & Clusters

This solution models your deployment hierarchy — from clusters down to service versions — and surfaces CVE vulnerability exposure across environments.

## What's Included

- **Entity types:** environment, release, service-version
- **Relationship type:** `environments` — powers a single catalog view of the full hierarchy
- **Sample entities:** 3 environments, 6 releases, 14 service versions across 4 services
- **Scorecard:** Am I Vulnerable? — surfaces CVE exposure per environment
- **Workflows:** Cortex workflows for creating environments and releases; GitHub Actions workflow for registering service versions on publish

## After Installing

1. Go to **Catalogs** in the Cortex UI
2. Create a new catalog using relationship type: `environments`
3. Set root entity type: `environment`

See the full README for MCP query examples and workflow setup.
