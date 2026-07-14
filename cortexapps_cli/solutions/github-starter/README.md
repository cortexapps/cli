---
name: GitHub Starter
description: Pre-configured scorecards for a GitHub-integrated Cortex workspace.
---

# GitHub Starter

This solution provides a starting point for teams using GitHub with Cortex.

## What's Included

- **GitHub Readiness Scorecard** — checks that services have GitHub repositories configured

## Prerequisites

- GitHub integration enabled in your Cortex workspace

## Installation

```
cortex solutions install -s github-starter
```

To overwrite existing resources:

```
cortex solutions install -s github-starter --force
```

## After Installing

Run `cortex scorecards list` to confirm the scorecard was imported, then navigate
to the Scorecards page in the Cortex UI to see scores across your services.
