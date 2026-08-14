---
name: Workday Integration
description: Configure the Cortex Workday integration with a sample org hierarchy from the fictional company Pied Piper (from the TV show Silicon Valley) to sync employees and teams into your service catalog.
---

# Workday Integration

Get the Cortex Workday integration running in minutes using a sample org hierarchy from the fictional company Pied Piper (from the TV show *Silicon Valley*). After install, trigger a sync to see employees and teams appear in your catalog — including the full team hierarchy.

## Org Hierarchy

```
PP: Pied Piper (Erlich Bachman)
├── PP: Engineering (Richard Hendricks)
│   ├── PP: Platform (Bertram Gilfoyle)
│   │   └── PP: Infrastructure (Nelson Bighetti)
│   └── PP: Frontend (Dinesh Chugtai)
└── PP: Operations (Jared Dunn)
    └── PP: People Ops (Monica Hall)
```

## What's Included

- **Pied Piper org data:** 7 employees across 4 levels of hierarchy (Erlich → Richard → Gilfoyle/Dinesh, Jared → Monica, Bachman → Big Head)
- **Integration config:** field mapping and report URL pre-configured, pointing at the hosted data
- **Setup script:** one-command configuration of the Cortex Workday integration via API

## Quick Start

1. Install the solution:

   ```
   cortex solutions install -s workday
   ```

2. Follow the post-install setup prompts, or run later:

   ```
   cortex solutions post-install -s workday
   ```

3. Trigger the import in Cortex:

   **Catalog → All Entities → Import Entities**

4. Check your team hierarchy to see the Pied Piper org chart.

## How It Works

The setup script calls the Cortex Workday integration API to configure a report URL pointing at `pied-piper-hierarchy.json` hosted in this repository. Cortex fetches the report and syncs employees and teams into your catalog on the next import run.

## Adapting to Real Workday Data

To point the integration at a real Workday RaaS report:

1. Go to **Settings → Integrations → Workday** in the Cortex UI
2. Update the **Report URL** to your Workday RaaS endpoint
3. Set your real **username** and **password**
4. Trigger a new import

The field mapping (`reportMappingV2`) in `data/configuration.json` matches the standard Cortex Workday report format and works unchanged for real Workday data that uses the same column names.
