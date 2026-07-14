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
            api_key = config[tenant].get("api_key")
            if not api_key:
                typer.echo(
                    f"Error: No api_key found for tenant '{tenant}' in config. Run 'cortex login' first."
                )
                raise typer.Exit(1)
        if not url:
            url = config[tenant].get("base_url", "https://api.getcortexapp.com")

    if not url:
        url = "https://api.getcortexapp.com"

    api_key = api_key.strip("\"' ")
    url = url.strip("\"' /")

    numeric_level = getattr(logging, log_level_str.upper(), logging.WARNING)
    return CortexClient(api_key, tenant, numeric_level, url, rate_limit)


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


def _print_readme(text: str) -> None:
    """Render README with left-justified headings and Rich Markdown body blocks."""
    # Strip YAML frontmatter
    body = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL).strip()

    heading_styles = {"# ": "bold", "## ": "bold underline", "### ": "bold"}
    pending: list[str] = []
    in_code_block = False

    def flush() -> None:
        block = "\n".join(pending).strip()
        if block:
            console.print(Markdown(block))
        pending.clear()

    for line in body.split("\n"):
        if line.startswith("```"):
            if not in_code_block:
                flush()
            in_code_block = not in_code_block
            continue

        if in_code_block:
            console.print(f"  [cyan]{line}[/cyan]" if line else "")
            continue

        for prefix, style in heading_styles.items():
            if line.startswith(prefix):
                flush()
                console.print(f"\n[{style}]{line[len(prefix):]}[/{style}]")
                break
        else:
            pending.append(line)

    flush()


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
    _print_readme(readme)


@app.command()
def install(
    ctx: typer.Context,
    solution: str = typer.Option(..., "--solution", "-s", help="Solution tag"),
    force: bool = typer.Option(False, "--force", help="Recreate entities if they already exist"),
    show_info: bool = typer.Option(True, "--info/--no-info", help="Show solution README after installing"),
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

    if show_info:
        readme = _get_readme(solution)
        if readme:
            console.print()
            _print_readme(readme)
