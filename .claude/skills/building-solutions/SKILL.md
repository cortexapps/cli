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
└── workflows/                        ← Cortex workflow YAML files (must include `tag:` field)
    └── <name>.yaml
```

The solution root IS the backup root — `backup.import_tenant` is called directly on this directory. Do not add a `backup/` subdirectory.

**File format rules (important):**
- `entity-types/` — **JSON only**. `entity_types.create` uses `json.loads`. Fields: `type`, `name`, `description`.
- `entity-relationship-types/` — **JSON only**. Fields: `tag`, `name`, `description`, `sourceTypes`, `targetTypes`.
- `catalog/` — **YAML** (OpenAPI format with `x-cortex-*` extensions). Must be **flat** — the importer only reads files at the top level, not subdirectories.
- `scorecards/` — YAML or JSON.
- `workflows/` — YAML or JSON, but **must include a `tag:` field** at the top level.

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

See `cortexapps_cli/solutions/github-starter/README.md` for a real example.

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
  x-cortex-groups:
    - groupName:value
  x-cortex-custom-data:
    key: value
  x-cortex-relationships:
    - tag: other-entity-tag
      type: relationship-type-tag
```

## Entity Type JSON Format

Entity types must be **JSON** (the CLI's `entity_types.create` uses `json.loads`):

```json
{
  "type": "my-type",
  "name": "My Type",
  "description": "What this entity type represents."
}
```

## Relationship Type JSON Format

Relationship types must be **JSON** and go in `entity-relationship-types/` (not `relationship-types/`):

```json
{
  "tag": "my-relationship",
  "name": "My Relationship",
  "description": "What this relationship means.",
  "sourceTypes": ["entity-type-a", "entity-type-b"],
  "targetTypes": ["entity-type-c"]
}
```

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

3. **Add backup content** — entity types (JSON), relationship types (JSON), catalog entities (flat YAML), scorecards, workflows (with `tag:` field).

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

6. **Smoke test via CLI:**
   ```bash
   poetry run cortex solutions list           # should show your solution
   poetry run cortex solutions info -s <tag>  # should render README
   ```

---

## How Install Works

`cortex solutions install -s <tag>` does exactly this:

```python
with as_file(_solutions_root() / tag) as solution_path:
    backup.import_tenant(ctx, directory=str(solution_path), force=force)
```

`backup.import_tenant` walks the directory and upserts every YAML file it recognizes into the user's Cortex instance. This means:
- Entity types and relationship types are created first
- Entities are upserted (created or updated)
- Scorecards are imported
- Files in `catalogs/` are skipped until catalog API support is added

---

## Catalog Placeholder Convention

Catalog creation is not yet supported via the backup API. Add a comment-only placeholder so users know what to do manually:

```yaml
# PLACEHOLDER — pending catalog API support in Cortex CLI
#
# After install, manually create the catalog:
#   1. Go to Catalogs in the Cortex UI
#   2. Click "New Catalog"
#   3. Select relationship type: <your-relationship-type>
#   4. Set root entity type: <your-root-type>
```

---

## Checklist for a New Solution

- [ ] Directory at `cortexapps_cli/solutions/<tag>/`
- [ ] `README.md` with valid YAML frontmatter (`name` + `description`)
- [ ] ASCII diagram in `## Overview` section of README
- [ ] All YAML files pass `yaml.safe_load`
- [ ] `cortex solutions list` shows the solution
- [ ] `cortex solutions info -s <tag>` renders correctly
- [ ] Commit with `feat: add <tag> solution`
