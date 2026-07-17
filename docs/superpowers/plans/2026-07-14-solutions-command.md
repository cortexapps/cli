# Solutions Command Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `solutions` subcommand with `list`, `info`, and `install` commands backed by Cortex backup bundles shipped inside the CLI package.

**Architecture:** Solutions live in `cortexapps_cli/solutions/<tag>/` (a Python package with `__init__.py`) as backup-format directories with a `README.md` containing YAML frontmatter. `importlib.resources.files()` resolves paths at runtime. The global auth callback skips client setup for `solutions` but stores raw credential params in `ctx.obj`; `install` builds its own client from those params. All three commands delegate to existing infrastructure (`backup.import_tenant`, Rich table, Rich Markdown).

**Tech Stack:** Python 3.11+, Typer, Rich (Table + Markdown), PyYAML (already in pyproject.toml), importlib.resources

## Global Constraints

- Python 3.11+ — use `str | None` union syntax, `match` statements are fine
- `importlib.resources.files()` for all solution path resolution — never `__file__` or `os.path`
- Flag naming: `--solution, -s` for solution tag; `--force` for install
- Rich for all output — `rich.table.Table` for list, `rich.markdown.Markdown` for info
- No new dependencies — all libraries already in pyproject.toml
- Follow existing Typer command module pattern (see `cortexapps_cli/commands/backup.py`)
- Tests use `tests/helpers/utils.py` `cli()` helper with `ReturnType.RAW` for exit code checks

---

### Task 1: Scaffold solutions package and sample bundle

**Files:**
- Create: `cortexapps_cli/solutions/__init__.py`
- Create: `cortexapps_cli/solutions/github-starter/README.md`
- Create: `cortexapps_cli/solutions/github-starter/scorecards/github-readiness.yaml`

**Interfaces:**
- Produces: `cortexapps_cli.solutions` importable Python package; `github-starter` bundle usable as a `backup import` directory

- [ ] **Step 1: Create the directory structure**

```bash
mkdir -p cortexapps_cli/solutions/github-starter/scorecards
touch cortexapps_cli/solutions/__init__.py
```

- [ ] **Step 2: Create `cortexapps_cli/solutions/github-starter/README.md`**

```markdown
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

## After Installing

Run `cortex scorecards list` to see the installed scorecards.
```

- [ ] **Step 3: Create `cortexapps_cli/solutions/github-starter/scorecards/github-readiness.yaml`**

```yaml
tag: github-readiness
name: GitHub Readiness
description: Basic checks for GitHub integration readiness
ladder:
  levels:
    - name: Bronze
      rank: 1
      description: Basic GitHub configuration
      color: "#CD7F32"
rules:
  - title: Has GitHub repository
    description: Service has a GitHub repository configured
    expression: "git != null"
    weight: 1
    level: Bronze
```

- [ ] **Step 4: Verify importlib.resources can locate the package**

```bash
poetry run python -c "
from importlib.resources import files
root = files('cortexapps_cli.solutions')
tags = [item.name for item in root.iterdir() if item.is_dir() and not item.name.startswith('_')]
print('Found solutions:', tags)
"
```

Expected output: `Found solutions: ['github-starter']`

- [ ] **Step 5: Commit**

```bash
git add cortexapps_cli/solutions/
git commit -m "feat: add solutions package scaffold with github-starter bundle"
```

---

### Task 2: Auth fix + cli.py wiring (infrastructure for all solutions commands)

**Files:**
- Modify: `cortexapps_cli/cli.py`
- Create: `cortexapps_cli/commands/solutions.py` (skeleton only — commands added in Tasks 3–5)

**Interfaces:**
- Consumes: `cortexapps_cli.solutions` package from Task 1
- Produces:
  - `global_callback` stores `_auth_params` dict in `ctx.obj` for the `solutions` group and returns early (no client setup, no auth error)
  - `solutions.app`: `typer.Typer` — registered in cli.py as `"solutions"`
  - Helper functions available to Tasks 3–5: `_solutions_root()`, `_list_solution_tags() -> list[str]`, `_parse_frontmatter(content: str) -> dict`, `_get_readme(tag: str) -> str | None`, `_build_client(ctx: typer.Context) -> CortexClient`

- [ ] **Step 1: Write a smoke test**

Create `tests/test_solutions.py`:
```python
from tests.helpers.utils import cli, ReturnType


def test_solutions_help():
    result = cli(["solutions", "--help"], return_type=ReturnType.RAW)
    assert result.exit_code == 0
    assert "solutions" in result.output.lower()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
poetry run pytest tests/test_solutions.py::test_solutions_help -v
```

Expected: FAILED — `No such command 'solutions'` or similar.

- [ ] **Step 3: Create `cortexapps_cli/commands/solutions.py` skeleton with helpers**

```python
import configparser
import logging
import os
import re
from importlib.resources import as_file, files

import typer
import yaml
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

from cortexapps_cli.cortex_client import CortexClient

app = typer.Typer(help="Solutions commands", no_args_is_help=True)
console = Console()


def _solutions_root():
    return files("cortexapps_cli.solutions")


def _list_solution_tags() -> list[str]:
    root = _solutions_root()
    return sorted(
        item.name
        for item in root.iterdir()
        if item.is_dir() and not item.name.startswith("_")
    )


def _parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter block from README content."""
    match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not match:
        return {}
    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}


def _get_readme(tag: str) -> str | None:
    """Return README.md content for a solution tag, or None if not found."""
    try:
        return (_solutions_root() / tag / "README.md").read_text(encoding="utf-8")
    except Exception:
        return None


def _build_client(ctx: typer.Context) -> CortexClient:
    """Build a CortexClient from auth params stored by global_callback."""
    params = ctx.obj.get("_auth_params", {})
    api_key = params.get("api_key")
    url = params.get("url")
    config_file = params.get(
        "config_file",
        os.path.join(os.path.expanduser("~"), ".cortex", "config"),
    )
    tenant = params.get("tenant", "default")
    log_level_str = params.get("log_level", "WARNING")
    rate_limit = params.get("rate_limit")

    if not os.path.isfile(config_file):
        if not api_key:
            typer.echo(
                "Error: Authentication required. Run 'cortex login' first or set CORTEX_API_KEY."
            )
            raise typer.Exit(1)
    else:
        config = configparser.ConfigParser()
        config.read(config_file)
        if not api_key:
            if tenant not in config:
                typer.echo(
                    f"Error: Tenant '{tenant}' not found in config. Run 'cortex login' first."
                )
                raise typer.Exit(1)
            api_key = config[tenant]["api_key"]
        if not url:
            url = config[tenant].get("base_url", "https://api.getcortexapp.com")

    if not url:
        url = "https://api.getcortexapp.com"

    api_key = api_key.strip("\"' ")
    url = url.strip("\"' /")

    numeric_level = getattr(logging, log_level_str.upper(), logging.WARNING)
    return CortexClient(api_key, tenant, numeric_level, url, rate_limit)
```

- [ ] **Step 4: Modify `cortexapps_cli/cli.py` — add auth skip for `solutions`**

In `global_callback`, find the existing `login` early-return:
```python
    if ctx.invoked_subcommand == "login":
        return
```

Replace with:
```python
    if ctx.invoked_subcommand == "login":
        return

    if ctx.invoked_subcommand == "solutions":
        ctx.obj["_auth_params"] = {
            "api_key": api_key,
            "url": url,
            "config_file": config_file,
            "tenant": tenant,
            "log_level": log_level,
            "rate_limit": rate_limit,
        }
        return
```

- [ ] **Step 5: Modify `cortexapps_cli/cli.py` — register solutions**

Add the import after the `scim` import line (keep alphabetical order):
```python
import cortexapps_cli.commands.solutions as solutions
```

Add the `add_typer` call between `secrets` and `teams` (alphabetical — "solutions" > "secrets", "solutions" < "teams"):
```python
app.add_typer(secrets.app, name="secrets")
app.add_typer(solutions.app, name="solutions")   # add this line
app.add_typer(teams.app, name="teams")
```

- [ ] **Step 6: Run test to verify it passes**

```bash
poetry run pytest tests/test_solutions.py::test_solutions_help -v
```

Expected: PASSED.

- [ ] **Step 7: Commit**

```bash
git add cortexapps_cli/commands/solutions.py cortexapps_cli/cli.py tests/test_solutions.py
git commit -m "feat: add solutions command skeleton, cli wiring, and auth bypass"
```

---

### Task 3: `list` command

**Files:**
- Modify: `cortexapps_cli/commands/solutions.py`
- Modify: `tests/test_solutions.py`

**Interfaces:**
- Consumes: `_list_solution_tags() -> list[str]`, `_get_readme(tag: str) -> str | None`, `_parse_frontmatter(content: str) -> dict` from Task 2
- Produces: `list_solutions` Typer command registered as `"list"` on `solutions.app`

- [ ] **Step 1: Add failing tests**

Append to `tests/test_solutions.py`:
```python
def test_solutions_list_shows_tag():
    result = cli(["solutions", "list"], return_type=ReturnType.RAW)
    assert result.exit_code == 0, result.output
    assert "github-starter" in result.output


def test_solutions_list_shows_name():
    result = cli(["solutions", "list"], return_type=ReturnType.RAW)
    assert result.exit_code == 0, result.output
    assert "GitHub Starter" in result.output


def test_solutions_list_shows_description():
    result = cli(["solutions", "list"], return_type=ReturnType.RAW)
    assert result.exit_code == 0, result.output
    assert "GitHub-integrated" in result.output
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
poetry run pytest tests/test_solutions.py::test_solutions_list_shows_tag tests/test_solutions.py::test_solutions_list_shows_name tests/test_solutions.py::test_solutions_list_shows_description -v
```

Expected: FAILED — `No such command 'list'`.

- [ ] **Step 3: Add `list_solutions` command to `cortexapps_cli/commands/solutions.py`**

Append after the `_build_client` function:
```python
@app.command("list")
def list_solutions(ctx: typer.Context):
    """List all available solutions."""
    tags = _list_solution_tags()
    table = Table(title="Available Solutions")
    table.add_column("Tag", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Description")
    for tag in tags:
        readme = _get_readme(tag)
        if readme is None:
            continue
        fm = _parse_frontmatter(readme)
        table.add_row(tag, fm.get("name", tag), fm.get("description", ""))
    console.print(table)
```

Note: the function is named `list_solutions` (not `list`) to avoid shadowing Python's built-in `list`. The `@app.command("list")` decorator registers it as the `list` subcommand.

- [ ] **Step 4: Run tests to verify they pass**

```bash
poetry run pytest tests/test_solutions.py::test_solutions_list_shows_tag tests/test_solutions.py::test_solutions_list_shows_name tests/test_solutions.py::test_solutions_list_shows_description -v
```

Expected: PASSED.

- [ ] **Step 5: Commit**

```bash
git add cortexapps_cli/commands/solutions.py tests/test_solutions.py
git commit -m "feat: add solutions list command"
```

---

### Task 4: `info` command

**Files:**
- Modify: `cortexapps_cli/commands/solutions.py`
- Modify: `tests/test_solutions.py`

**Interfaces:**
- Consumes: `_get_readme(tag: str) -> str | None`, `_list_solution_tags() -> list[str]`, `console: Console`, `Markdown` from Task 2
- Produces: `info` Typer command on `solutions.app`; accepts `--solution/-s` (required string)

- [ ] **Step 1: Add failing tests**

Append to `tests/test_solutions.py`:
```python
def test_solutions_info_known_tag():
    result = cli(["solutions", "info", "-s", "github-starter"], return_type=ReturnType.RAW)
    assert result.exit_code == 0, result.output
    assert "GitHub Starter" in result.output


def test_solutions_info_unknown_tag():
    result = cli(["solutions", "info", "-s", "nonexistent-xyz-abc"], return_type=ReturnType.RAW)
    assert result.exit_code == 1
    assert "not found" in result.output.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
poetry run pytest tests/test_solutions.py::test_solutions_info_known_tag tests/test_solutions.py::test_solutions_info_unknown_tag -v
```

Expected: FAILED — `No such command 'info'`.

- [ ] **Step 3: Add `info` command to `cortexapps_cli/commands/solutions.py`**

Append after `list_solutions`:
```python
@app.command()
def info(
    ctx: typer.Context,
    solution: str = typer.Option(..., "--solution", "-s", help="Solution tag"),
):
    """Show README for a solution."""
    readme = _get_readme(solution)
    if readme is None:
        avail = ", ".join(_list_solution_tags())
        typer.echo(f"Error: Solution '{solution}' not found. Available: {avail}")
        raise typer.Exit(1)
    console.print(Markdown(readme))
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
poetry run pytest tests/test_solutions.py::test_solutions_info_known_tag tests/test_solutions.py::test_solutions_info_unknown_tag -v
```

Expected: PASSED.

- [ ] **Step 5: Commit**

```bash
git add cortexapps_cli/commands/solutions.py tests/test_solutions.py
git commit -m "feat: add solutions info command"
```

---

### Task 5: `install` command

**Files:**
- Modify: `cortexapps_cli/commands/solutions.py`
- Modify: `tests/test_solutions.py`

**Interfaces:**
- Consumes: `_list_solution_tags() -> list[str]`, `_solutions_root()`, `_build_client(ctx) -> CortexClient`, `as_file` from Task 2; `backup.import_tenant(ctx, directory: str, force: bool)` from `cortexapps_cli/commands/backup.py`
- Produces: `install` Typer command on `solutions.app`; accepts `--solution/-s` (required string), `--force` (bool, default False)

- [ ] **Step 1: Add failing tests**

Append to `tests/test_solutions.py`:
```python
def test_solutions_install_unknown_tag():
    # Unknown-tag check runs before auth check, so no credentials needed
    result = cli(["solutions", "install", "-s", "nonexistent-xyz-abc"], return_type=ReturnType.RAW)
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


def test_solutions_install_no_auth():
    # Known tag, but no credentials configured — should fail with auth error
    # This test only applies when no config file or CORTEX_API_KEY is present.
    # Skip if the test environment has credentials set up.
    import os
    if os.path.isfile(os.path.join(os.path.expanduser("~"), ".cortex", "config")):
        import pytest
        pytest.skip("Skipping: credentials are configured in this environment")
    result = cli(["solutions", "install", "-s", "github-starter"], return_type=ReturnType.RAW)
    assert result.exit_code == 1
    assert "authentication required" in result.output.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
poetry run pytest tests/test_solutions.py::test_solutions_install_unknown_tag tests/test_solutions.py::test_solutions_install_no_auth -v
```

Expected: FAILED — `No such command 'install'`.

- [ ] **Step 3: Add `install` command to `cortexapps_cli/commands/solutions.py`**

Append after `info`. This import goes at the top of the function body (lazy import avoids circular imports):
```python
@app.command()
def install(
    ctx: typer.Context,
    solution: str = typer.Option(..., "--solution", "-s", help="Solution tag"),
    force: bool = typer.Option(False, "--force", help="Recreate entities if they already exist"),
):
    """Install a solution into the current Cortex workspace."""
    if solution not in _list_solution_tags():
        avail = ", ".join(_list_solution_tags())
        typer.echo(f"Error: Solution '{solution}' not found. Available: {avail}")
        raise typer.Exit(1)

    ctx.obj["client"] = _build_client(ctx)

    import cortexapps_cli.commands.backup as backup

    with as_file(_solutions_root() / solution) as solution_path:
        backup.import_tenant(ctx, directory=str(solution_path), force=force)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
poetry run pytest tests/test_solutions.py::test_solutions_install_unknown_tag tests/test_solutions.py::test_solutions_install_no_auth -v
```

Expected: PASSED (or second test skipped if credentials are configured).

- [ ] **Step 5: Run all solutions tests**

```bash
poetry run pytest tests/test_solutions.py -v
```

Expected: all PASSED (or skipped where appropriate).

- [ ] **Step 6: Quick manual smoke test**

```bash
poetry run cortex solutions --help
poetry run cortex solutions list
poetry run cortex solutions info -s github-starter
```

Expected:
- `--help` shows `list`, `info`, `install` subcommands
- `list` renders a Rich table with `github-starter` row
- `info` renders the README in Rich Markdown with styled headers

- [ ] **Step 7: Commit**

```bash
git add cortexapps_cli/commands/solutions.py tests/test_solutions.py
git commit -m "feat: add solutions install command"
```
