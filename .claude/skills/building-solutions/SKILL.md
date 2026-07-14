---
name: building-solutions
description: Use when creating a new Cortex solution bundle, adding content to an existing solution, or understanding how solutions are packaged and installed via `cortex solutions install`. Triggers on "new solution", "add a solution", "build a solution", "package a solution", or any work inside `cortexapps_cli/solutions/`.
---

# Building & Packaging a Cortex Solution

A **solution** is a self-contained bundle of Cortex backup YAML shipped inside the CLI package. When a user runs `cortex solutions install -s <tag>`, the CLI calls `backup.import_tenant` on the solution directory, creating all entities, scorecards, and relationships in their Cortex instance.

---

## Directory Structure

Every solution lives at `cortexapps_cli/solutions/<tag>/` and is a valid Cortex backup directory:

```
cortexapps_cli/solutions/<tag>/
├── README.md                         ← required — YAML frontmatter + ASCII diagram
├── entity-types/                     ← custom entity type definitions (JSON files)
│   └── <type>.json
├── entity-relationship-types/        ← custom relationship type definitions (JSON files)
│   └── <type>.json
├── catalog/                          ← sample or seed entities (flat — no subdirs)
│   └── <tag>.yaml
├── scorecards/                       ← scorecard definitions
│   └── <tag>.yaml
└── workflows/                        ← Cortex workflow YAML files
    └── <name>.yaml
```

The solution root IS the backup root — `backup.import_tenant` is called directly on this directory. Do not add a `backup/` subdirectory.

**Do NOT include `.gitkeep` files.** The importer tries to parse every file it finds.

**File format rules — these are hard requirements:**
- `entity-types/` — **JSON only**. `entity_types.create` uses `json.loads`. Fields: `type`, `name`, `description`.
- `entity-relationship-types/` — **JSON only**. Must include `definitionLocation`, `sourcesFilter`, `destinationsFilter`, `inheritances`. See format below.
- `catalog/` — **YAML** (OpenAPI format with `x-cortex-*` extensions). Must be **flat** — the importer only reads files at the top level, not subdirectories.
- `scorecards/` — YAML or JSON.
- `workflows/` — YAML or JSON. Must include `tag:`, `filter:`, and `actions:` fields. See format below.

---

## README.md Format

The README.md **must** have YAML frontmatter as the very first block. This is how `cortex solutions list` populates the Name and Description columns.

```markdown
---
name: Human Readable Name
description: One-sentence description shown in `cortex solutions list`.
---

# Human Readable Name

Brief intro paragraph.

## Overview

\```
ASCII diagram showing the key relationships or concepts
\```

## What's Included

- **Entity types:** list them
- **Scorecards:** list them

## Installation

\```
cortex solutions install -s <tag>
\```

## After Installing

Steps the user must take manually after install (e.g. create a Catalog in the UI).
```

---

## Entity YAML Format

All entities use OpenAPI 3.0 format with `x-cortex-*` extensions:

```yaml
openapi: "3.0.0"
info:
  title: my-entity
  x-cortex-tag: my-entity
  x-cortex-type: <entity-type-tag>
  x-cortex-description: Human readable description
  x-cortex-definition: {}      ← REQUIRED for custom entity types (e.g. non-service/domain/team)
  x-cortex-groups:
    - groupName:value
  x-cortex-custom-data:
    key: value
  x-cortex-relationships:
    - type: relationship-type-tag
      destinations:
        - tag: child-entity-tag
```

**`x-cortex-definition: {}`** — Required for custom entity types (anything not service, domain, or team). Omitting it causes "Standard cortex tags: Definition is required" on import.

---

## Entity Relationship Format in Catalog YAML

The `x-cortex-relationships` block uses **`type`** (not `tag`) for the relationship type name, and **`destinations`** or **`sources`** for the connected entities:

```yaml
x-cortex-relationships:
  - type: my-relationship-type    ← relationship TYPE tag (not the connected entity tag)
    destinations:                 ← use 'destinations' if this entity is the SOURCE
      - tag: child-entity-tag
      - tag: another-child-tag
```

**Which direction to use** depends on the relationship type's `definitionLocation`:
- `definitionLocation: SOURCE` — the SOURCE entity defines the relationship using `destinations`. The source entity lists its children.
- `definitionLocation: DESTINATION` — the DESTINATION entity defines the relationship using `sources`. The child entity points to its parent.

**Choose SOURCE when** the parent entity should enumerate its children (e.g. environment lists its releases). All child entities will be destinations.

**The relationship type's `sourcesFilter` and `destinationsFilter`** control which entity types are allowed on each end. Violations produce errors like "cannot have destinations of type X" if you point to the wrong type.

---

## Entity Type JSON Format

Entity types must be **JSON** (the CLI's `entity_types.create` uses `json.loads`):

```json
{
  "type": "my-type",
  "name": "My Type",
  "description": "What this entity type represents."
}
```

**Note:** If a custom entity type with the same `type` tag already exists in the tenant, the importer silently skips creation. The existing definition may differ from yours.

---

## Relationship Type JSON Format

Relationship types must be **JSON**, go in `entity-relationship-types/` (not `relationship-types/`), and include all required fields:

```json
{
  "tag": "my-relationship",
  "name": "My Relationship",
  "description": "What this relationship means.",
  "definitionLocation": "SOURCE",
  "isSingleSource": false,
  "isSingleDestination": false,
  "allowCycles": false,
  "sourcesFilter": {
    "include": true,
    "types": ["source-entity-type"],
    "providers": []
  },
  "destinationsFilter": {
    "include": true,
    "types": ["destination-entity-type"],
    "providers": []
  },
  "inheritances": []
}
```

**`definitionLocation`** — required. Values: `"SOURCE"`, `"DESTINATION"`, `"BOTH"`.
- `SOURCE`: the source entity's YAML defines the relationship (uses `destinations:` in entity YAML)
- `DESTINATION`: the destination entity's YAML defines the relationship (uses `sources:` in entity YAML)

**`inheritances`** — required, even if empty (`[]`).

**`sourcesFilter` / `destinationsFilter`** — required. Set `include: true` with specific `types` to restrict which entity types can be on each end, or `include: false` with `types: []` for unrestricted.

---

## Workflow YAML Format

Workflows must include `tag`, `filter`, and `actions`. The format is the Cortex workflow API object, **not** a DSL with `trigger`/`inputs`/`steps`.

```yaml
tag: my-workflow
name: My Workflow
description: What this workflow does.
filter:
  type: GLOBAL          # or ENTITY for entity-scoped workflows
isDraft: true
actions:
  - name: Collect Inputs
    slug: collect-inputs
    isRootAction: true
    outgoingActions:
      - next-action-slug
    schema:
      type: USER_INPUT
      inputs:
        - name: Field Name
          key: fieldKey
          description: Description shown to user
          required: true
          type: INPUT_FIELD        # or SELECT_FIELD for dropdown
          options:                 # only for SELECT_FIELD
            - option1
            - option2
      inputOverrides: []
      jsValidatorScript: null
  - name: Create Entity
    slug: create-entity
    isRootAction: false
    outgoingActions: []
    schema:
      type: ADVANCED_HTTP_REQUEST
      actionIdentifier: cortex.createOrUpdateEntity
      integrationAlias: null
      inputs:
        mode: CREATE              # or UPSERT
        dryRun: false
        body: |
          openapi: "3.0.0"
          info:
            title: "{{actions.collect-inputs.outputs.fieldKey}}"
            x-cortex-tag: "{{actions.collect-inputs.outputs.fieldKey}}"
            x-cortex-type: my-type
            x-cortex-definition: {}
```

**Template syntax:** `{{actions.<slug>.outputs.<key>}}` to reference previous action outputs. Use `{{{...}}}` (triple braces) for raw/unescaped values.

**Available action identifiers:**
- `cortex.createOrUpdateEntity` — create or upsert a Cortex entity. Inputs: `body` (YAML string), `mode` (CREATE/UPSERT), `dryRun`.
- `cortex.createOrPatchEntity` — patch an existing entity. Inputs: `body`, `dryRun`, `appendArrays`, `failIfEntityDoesNotExist`.
- `cortex.addCustomMetricsDataPoint` — push a custom metric. Inputs: `value`, `entityId`, `timestamp`, `metricsKey`.
- `github.getFile` — fetch a file from GitHub. Inputs: `path`, `repo`.
- `github.createRelease` — create a GitHub release. Inputs: `repo`, `tagName`, `name`, `body`, `draft`, `prerelease`.

**GitHub workflow limitation:** `github.*` actions require a configured GitHub integration alias in the target tenant. Workflows using GitHub actions will fail import in tenants without it. Either make the workflow a stub (USER_INPUT only) or document this requirement in the README.

**`filter.type`:**
- `GLOBAL` — workflow runs globally, not scoped to an entity
- `ENTITY` — workflow runs on a specific entity; can access `{{context.entity.*}}`

---

## Scorecard YAML Format

```yaml
tag: my-scorecard
name: My Scorecard
description: What this scorecard measures.
filter:
  entityType: <entity-type-tag>
rules:
  - title: Rule title
    description: What passes/fails and why.
    weight: 1
    expression: "git != null"
```

---

## Adding a New Solution

1. **Create the directory:**
   ```bash
   mkdir -p cortexapps_cli/solutions/<tag>/{entity-types,entity-relationship-types,catalog,scorecards,workflows}
   ```

2. **Write README.md** with YAML frontmatter (name + description required).

3. **Add backup content** — entity types (JSON), relationship types (JSON), catalog entities (flat YAML), scorecards, workflows.

4. **Verify `importlib.resources` discovers it:**
   ```bash
   poetry run python -c "
   from importlib.resources import files
   root = files('cortexapps_cli.solutions')
   print([i.name for i in root.iterdir() if i.is_dir() and not i.name.startswith('_')])
   "
   ```
   Your solution tag should appear in the list.

5. **Validate all YAML:**
   ```bash
   python3 -c "
   import yaml, glob
   for f in glob.glob('cortexapps_cli/solutions/<tag>/**/*.yaml', recursive=True):
       yaml.safe_load(open(f))
       print('OK:', f)
   "
   ```

6. **Test each resource type individually before running the full install:**
   ```bash
   poetry run cortex entity-types create -f cortexapps_cli/solutions/<tag>/entity-types/<type>.json
   poetry run cortex entity-relationship-types create -f cortexapps_cli/solutions/<tag>/entity-relationship-types/<rel>.json
   poetry run cortex catalog create -f cortexapps_cli/solutions/<tag>/catalog/<entity>.yaml
   poetry run cortex workflows create -f cortexapps_cli/solutions/<tag>/workflows/<workflow>.yaml
   ```
   Fix errors before running `solutions install`.

7. **Smoke test via CLI:**
   ```bash
   poetry run cortex solutions list           # should show your solution
   poetry run cortex solutions info -s <tag>  # should render README
   poetry run cortex solutions install -s <tag>
   ```

---

## How Install Works

`cortex solutions install -s <tag>` does exactly this:

```python
with as_file(_solutions_root() / tag) as solution_path:
    backup.import_tenant(ctx, directory=str(solution_path), force=force)
```

`backup.import_tenant` processes directories in this order:
1. `ip-allowlist/`
2. `entity-types/` — JSON files
3. `entity-relationship-types/` — JSON files
4. `catalog/` — YAML/JSON entities (flat, parallel import + two-pass for relationships)
5. `entity-relationships/` — JSON
6. `plugins/`
7. `scorecards/` — YAML/JSON
8. `workflows/` — YAML/JSON

---

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `JSONDecodeError - Expecting value` | Entity type file is YAML, not JSON | Convert to JSON |
| `missing required field(s): definitionLocation` | Relationship type missing required fields | Add `definitionLocation`, `sourcesFilter`, `destinationsFilter`, `inheritances` |
| `missing required field(s): inheritances` | Relationship type JSON missing field | Add `"inheritances": []` |
| `Relationship type #1 must contain at least one of sources or destinations` | Old format `{tag:..., type:...}` used | Use `{type: rel-type, destinations: [{tag:...}]}` |
| `Relationship type #1 is missing required type field` | Using `tag:` instead of `type:` for relationship | Change outer key from `tag:` to `type:` |
| `Relationships of type X must be defined by the SOURCE entity` | Entity has relationship but wrong `definitionLocation` | Relationship must be on source entities (if SOURCE) or destination entities (if DESTINATION) |
| `cannot have destinations of type X` | Wrong entity type in destinations | sourcesFilter/destinationsFilter restrict which types are allowed on each end |
| `Standard cortex tags: Definition is required` | Custom entity missing `x-cortex-definition` | Add `x-cortex-definition: {}` to entity YAML |
| `missing required field(s): filter` | Workflow missing `filter:` field | Add `filter: {type: GLOBAL}` or `{type: ENTITY}` |
| `missing required field(s): actions` | Workflow missing `actions:` field | Add `actions: []` or populate with real actions |
| `Duplicate field 'filter'` | Script added filter twice | Remove duplicate from workflow YAML |
| `Invalid Github configuration alias` | Workflow uses `github.*` action but no GitHub integration configured in tenant | Remove GitHub action or document as manual step |
| `.gitkeep` parse errors | Empty placeholder files are parsed | Remove all `.gitkeep` files from solution |

---

## Checklist for a New Solution

- [ ] Directory at `cortexapps_cli/solutions/<tag>/`
- [ ] `README.md` with valid YAML frontmatter (`name` + `description`)
- [ ] ASCII diagram in `## Overview` section of README
- [ ] No `.gitkeep` files anywhere in the solution
- [ ] Entity types as JSON with `type`, `name`, `description`
- [ ] Relationship types as JSON with all required fields including `definitionLocation` and `inheritances`
- [ ] Catalog entities are flat (no subdirectories), custom types have `x-cortex-definition: {}`
- [ ] Entity relationships use `type:` (not `tag:`) and `destinations:`/`sources:` consistent with `definitionLocation`
- [ ] Workflows have `tag:`, `filter:`, and `actions:` fields
- [ ] Each resource type tested individually before running full install
- [ ] `cortex solutions list` shows the solution
- [ ] `cortex solutions info -s <tag>` renders correctly
- [ ] `cortex solutions install -s <tag>` completes with 0 failures
- [ ] Commit with `feat: add <tag> solution`
