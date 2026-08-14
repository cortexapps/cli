---
name: Workday Integration
description: Configure the Cortex Workday integration with a sample org hierarchy from the fictional company Pied Piper (from the TV show Silicon Valley) to sync employees and teams into your service catalog.
---

# Workday Integration

Get the Cortex Workday integration running in minutes using a sample org hierarchy from the fictional company Pied Piper (from the TV show *Silicon Valley*). After install, trigger a sync to see employees and teams appear in your catalog — including the full team hierarchy.

## Data Model

```
  ┌──────────────────────┐     ┌──────────────────────┐     ┌──────────────────────┐
  │   Workday Report     │────▶│  Cortex Integration  │────▶│   Team Catalog       │
  │   (JSON / RaaS)      │     │   (field mapping)    │     │   + Members          │
  └──────────────────────┘     └──────────────────────┘     └──────────────────────┘

  Sample: Pied Piper supervisory org (Silicon Valley)

  PP: Pied Piper (Erlich Bachman)
  ├── PP: Engineering (Richard Hendricks)
  │   ├── PP: Platform (Bertram Gilfoyle)
  │   │   └── PP: Infrastructure (Nelson Bighetti)
  │   └── PP: Frontend (Dinesh Chugtai)
  └── PP: Operations (Jared Dunn)
      └── PP: People Ops (Monica Hall)
```

## After Installing

Trigger the sync in Cortex to import the Pied Piper org hierarchy:

**Catalog → All Entities → Import Entities → Workday → Sync Entities → Next Step**

You should see 7 teams appear in your catalog with the full hierarchy:

```
PP: Pied Piper (Erlich Bachman)
├── PP: Engineering (Richard Hendricks)
│   ├── PP: Platform (Bertram Gilfoyle)
│   │   └── PP: Infrastructure (Nelson Bighetti)
│   └── PP: Frontend (Dinesh Chugtai)
└── PP: Operations (Jared Dunn)
    └── PP: People Ops (Monica Hall)
```

Workday reports can be customized to match your org structure. The configuration defines which report columns map to employee fields, team identity, and the parent-child hierarchy — so the integration works with any supervisory org report that follows the same shape.

## What's Included

- **Pied Piper org data:** 7 employees across 4 levels of hierarchy (Erlich → Richard → Gilfoyle/Dinesh, Jared → Monica, Gilfoyle → Big Head)
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

   **Catalog → All Entities → Import Entities → Workday → Sync Entities → Next Step**

4. Check your team hierarchy to see the Pied Piper org chart.

## How It Works

The setup script calls the Cortex Workday integration API to configure a report URL pointing at the bundled Pied Piper supervisory org data. Cortex fetches the report and syncs employees and teams into your catalog on the next import run.

## Report Format

Each entry in the Workday report represents one employee. The `Workteam_Group` array lists every team the employee belongs to, with hierarchy encoded as a `parentTeamId` pointing to the parent team's `teamName`. Root teams use `"parentTeamId": "NONE"`. Managers have a `Team_Managed` field matching their team's `teamName`.

```json
{
  "Report_Entry": [
    {
      "Email": "erlich.bachman@piedpiper.com",
      "Employee_ID": "PP-100000",
      "First_Name": "Erlich",
      "Last_Name": "Bachman",
      "Managers_Email": "erlich.bachman@piedpiper.com",
      "employeeRole": "CEO",
      "Workteam_Group": [
        {
          "teamName": "PP: Pied Piper",
          "teamDisplayName": "PP: Pied Piper",
          "parentTeamId": "NONE",
          "Team_Managed": "PP: Pied Piper"
        }
      ]
    },
    ...
  ]
}
```

## Field Mapping

The `data/configuration.json` file tells Cortex how to interpret the report columns. It maps employee identity fields, defines the team list array, and specifies which fields encode the parent-child hierarchy:

```json
{
  "username": "ISU_Cortex",
  "password": "<your-password>",
  "ownershipReportUrl": "<your-report-url>",
  "reportMappingV2": {
    "email":       { "columnName": "Email" },
    "employeeId":  { "columnName": "Employee_ID" },
    "firstName":   { "columnName": "First_Name" },
    "lastName":    { "columnName": "Last_Name" },
    "employeeRole":{ "columnName": "employeeRole" },
    "managerEmail": null,
    "rootTeams": [],
    "teamListFields": {
      "teamListKey": { "columnName": "Workteam_Group" },
      "teamId":      { "columnName": "teamName" },
      "teamName":    { "columnName": "teamDisplayName" },
      "hierarchy": {
        "fieldOnParentNode": { "columnName": "teamName", "isList": false },
        "fieldOnChildNode":  { "columnName": "parentTeamId" }
      },
      "teamEmployeeManages": { "columnName": "Team_Managed" }
    },
    "type": "ONE_EMPLOYEE_MULTIPLE_TEAMS"
  }
}
```

## Adapting to Real Workday Data

To connect your own Workday report, go to **Settings → Integrations → Workday** in the Cortex UI and update the Report URL, username, and password. The field mapping in `data/configuration.json` works unchanged for any Workday supervisory org report that uses the same column names.
