# Solutions Command Design

**Date:** 2026-07-14
**Branch:** team-roles (to be implemented on a feature branch)

## Overview

Add a `solutions` subcommand to the Cortex CLI that exposes pre-packaged Cortex configurations (entities, scorecards, plugins, workflows, etc.) bundled directly in the CLI package. Users can list available solutions, read their documentation, and install them into a Cortex workspace.

## File Structure

Solutions are stored inside the Python package so they are available on disk with every install (pip, homebrew, poetry):

```
cortexapps_cli/
  solutions/
    __init__.py
    <solution-tag>/
      README.md          ← frontmatter + full documentation
      catalog/           ← backup directory structure
      scorecards/
      plugins/
      workflows/
      entity-types/
      ...
  commands/
    solutions.py         ← new command module
```

Each solution directory mirrors the structure produced by `cortex backup export`, so it can be passed directly to `backup import`.

## README Frontmatter Format

Each solution's `README.md` begins with a YAML frontmatter block:

```markdown
---
name: GitHub Starter
description: Pre-configured entities and scorecards for a GitHub-integrated workspace.
---

# GitHub Starter

Full documentation follows...
```

The `name` and `description` fields are required. The `list` command reads only the frontmatter; `info` renders the full file.

## Commands

### `cortex solutions list`

Lists all bundled solutions as a Rich table with columns: **tag**, **name**, **description**.

- Discovers solutions by scanning `cortexapps_cli/solutions/` via `importlib.resources`
- Reads and parses the YAML frontmatter from each `README.md`
- Renders output with `rich.table.Table`
- Does not require API authentication (no `ctx.obj["client"]` needed)

### `cortex solutions info -s <tag>`

Displays the full README for a solution using Rich Markdown rendering.

- Flag: `--solution, -s` (required) — solution tag slug
- Resolves path via `importlib.resources`
- Renders via `rich.markdown.Markdown` and `rich.console.Console`
- Exits with error if tag not found

### `cortex solutions install -s <tag> [--force]`

Installs a solution into the current Cortex workspace by delegating to `backup.import_tenant`.

- Flag: `--solution, -s` (required) — solution tag slug
- Flag: `--force` — passed through to `backup.import_tenant`; recreates entities that already exist (default: fail on conflict)
- Resolves the solution directory path via `importlib.resources`
- Calls `backup.import_tenant(ctx, directory=str(path), force=force)` directly — no subprocess
- Exits with error if tag not found
- Inherits all backup import output and error handling

## Architecture

### Path Resolution

Use `importlib.resources` to locate solution directories at runtime:

```python
from importlib.resources import files

solutions_root = files("cortexapps_cli.solutions")
solution_path = solutions_root / solution_tag
```

This works correctly whether the package is installed as a directory (pip, poetry, homebrew) or accessed from source.

### Integration with backup.import_tenant

`solutions install` calls `backup.import_tenant` as a plain Python function:

```python
import cortexapps_cli.commands.backup as backup

backup.import_tenant(ctx, directory=str(solution_path), force=force)
```

No refactoring of `backup.py` is needed. The `import_tenant` function already accepts `ctx`, `directory`, and `force`.

### solutions.py command module

Follows the standard pattern used by all other command modules:

```python
app = typer.Typer(help="Solutions commands", no_args_is_help=True)

@app.command()
def list(ctx: typer.Context): ...

@app.command()
def info(ctx: typer.Context, solution: str = typer.Option(..., "--solution", "-s")): ...

@app.command()
def install(ctx: typer.Context, solution: str = typer.Option(..., "--solution", "-s"), force: bool = ...): ...
```

### Registration in cli.py

Add to `cli.py` in alphabetical order (between `scim` and `scorecards`):

```python
import cortexapps_cli.commands.solutions as solutions
# ...
app.add_typer(solutions.app, name="solutions")
```

## Auth Consideration

`solutions list` and `solutions info` do not call the Cortex API, but the global callback in `cli.py` raises an error if no API key is configured. To allow these commands to work without credentials, `global_callback` must skip auth setup when the invoked subcommand is `solutions` (similar to how it already skips for `login`):

```python
if ctx.invoked_subcommand in ("login", "solutions"):
    return
```

Since `ctx.invoked_subcommand` only gives the top-level command name (`"solutions"`), the entire solutions group is skipped. The `install` command must then explicitly check that the client was set up:

```python
if not ctx.obj or "client" not in ctx.obj:
    typer.echo("Error: Authentication required. Run 'cortex login' first.")
    raise typer.Exit(1)
```

## Error Handling

- Unknown solution tag: print a clear error with `typer.echo` and `raise typer.Exit(1)`. List available tags.
- Malformed or missing frontmatter: skip the solution in `list` and print a warning; abort `info`/`install` with an error.
- Install failures: inherited from `backup.import_tenant` (already prints per-file errors and a summary).

## Packaging

`cortexapps_cli/solutions/` must be included in the package. Since `pyproject.toml` uses Poetry with `packages = [{include = "cortexapps_cli"}]`, subdirectories are included automatically. The `__init__.py` file ensures Python treats it as a package for `importlib.resources`.

## Testing

- `list` can be tested without a live API (no auth required)
- `info` can be tested without a live API
- `install` tests require a live API (same as other backup tests) — mark serial if needed
- At minimum: one smoke test solution bundled in the package for integration testing

## Out of Scope

- Remote/downloadable solutions (all solutions are bundled in the CLI)
- Solution versioning
- Solution uninstall
- Solution update checking
