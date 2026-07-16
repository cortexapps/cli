import configparser
import contextlib
import io
import json
import logging
import os
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from importlib.resources import as_file, files
from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table

from cortexapps_cli.cortex_client import CortexClient

try:
    import select as _select
    import termios as _termios
    import tty as _tty
    _TTY_SUPPORT = True
except ImportError:
    _TTY_SUPPORT = False

app = typer.Typer(help="Solutions commands", no_args_is_help=True)
console = Console()


class _ToggleableCapture:
    """Stdout proxy that buffers all output and optionally mirrors it live."""

    def __init__(self, real_stdout):
        self._real = real_stdout
        self._buf = io.StringIO()
        self._on = False
        self._shown_pos = 0  # chars already written to real_stdout
        self._lock = threading.Lock()

    def write(self, text: str) -> int:
        with self._lock:
            self._buf.write(text)
            if self._on:
                self._real.write(text)
                self._real.flush()
                self._shown_pos += len(text)
        return len(text)

    def flush(self) -> None:
        pass

    def toggle(self) -> bool:
        with self._lock:
            self._on = not self._on
            if self._on:
                # Flush everything buffered since the last toggle-on
                content = self._buf.getvalue()
                pending = content[self._shown_pos:]
                if pending:
                    self._real.write(pending)
                    self._real.flush()
                self._shown_pos = len(content)
            return self._on

    def getvalue(self) -> str:
        return self._buf.getvalue()


def _run_import_with_toggle(fn) -> str:
    """Run fn() capturing stdout. On a TTY, Ctrl+o toggles live output."""
    real_stdout = sys.stdout
    capture = _ToggleableCapture(real_stdout)

    if not (_TTY_SUPPORT and sys.stdin.isatty()):
        with contextlib.redirect_stdout(capture):
            fn()
        return capture.getvalue()

    done = threading.Event()
    fd = sys.stdin.fileno()
    old_settings = _termios.tcgetattr(fd)

    def _listen() -> None:
        try:
            # setcbreak() keeps IEXTEN, which makes the kernel intercept \x0f
            # as VDISCARD before it reaches the app. Manually disable ECHO,
            # ICANON, and IEXTEN while keeping OPOST (output processing) and
            # ISIG (so Ctrl+c still works).
            mode = _termios.tcgetattr(fd)
            mode[3] &= ~(_termios.ECHO | _termios.ICANON | _termios.IEXTEN)
            mode[6][_termios.VMIN] = 1
            mode[6][_termios.VTIME] = 0
            _termios.tcsetattr(fd, _termios.TCSAFLUSH, mode)
            while not done.is_set():
                r, _, _ = _select.select([fd], [], [], 0.05)
                if r:
                    ch = os.read(fd, 1)
                    if ch == b"\x0f":  # Ctrl+o
                        on = capture.toggle()
                        label = "on" if on else "off"
                        real_stdout.write(f"  -- output {label} --\n")
                        real_stdout.flush()
        except Exception:
            pass

    t = threading.Thread(target=_listen, daemon=True)
    t.start()
    try:
        with contextlib.redirect_stdout(capture):
            fn()
    finally:
        done.set()
        t.join(timeout=0.5)
        try:
            _termios.tcsetattr(fd, _termios.TCSADRAIN, old_settings)
        except Exception:
            pass

    return capture.getvalue()


@app.callback()
def solutions_callback(
    ctx: typer.Context,
    solutions_dir: str | None = typer.Option(
        None,
        "--solutions-dir",
        help="Path to a custom solutions directory (overrides the built-in solutions).",
        show_default=False,
    ),
) -> None:
    ctx.ensure_object(dict)
    if solutions_dir:
        ctx.obj["solutions_dir"] = solutions_dir


def _solutions_root(path: str | None = None):
    if path:
        return Path(path)
    return files("cortexapps_cli.solutions")


def _list_solution_tags(path: str | None = None) -> list[str]:
    root = _solutions_root(path)
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


def _get_readme(tag: str, path: str | None = None) -> str | None:
    """Return README.md content for a solution tag, or None if not found."""
    try:
        return (_solutions_root(path) / tag / "README.md").read_text(encoding="utf-8")
    except Exception:
        return None


def _extract_first_codeblock(text: str) -> str | None:
    """Return content of the first fenced code block."""
    m = re.search(r"```[^\n]*\n(.*?)```", text, re.DOTALL)
    return m.group(1).rstrip("\n") if m else None


def _extract_section(text: str, heading: str) -> str | None:
    """Return the body of the first section with the given heading text."""
    body = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL)
    pattern = re.compile(r"^(#{1,3})\s+" + re.escape(heading) + r"\s*$", re.MULTILINE)
    m = pattern.search(body)
    if not m:
        return None
    level = len(m.group(1))
    start = m.end()
    next_heading = re.compile(r"^#{1," + str(level) + r"}\s", re.MULTILINE)
    m2 = next_heading.search(body, start + 1)
    end = m2.start() if m2 else len(body)
    return body[start:end].strip()


def _get_ui_url(ctx: typer.Context) -> str:
    """Derive the Cortex app UI URL from the configured API URL."""
    params = ctx.obj.get("_auth_params", {})
    api_url = params.get("url", "https://api.getcortexapp.com").strip("\"' /")
    if api_url == "https://api.getcortexapp.com":
        return "https://app.getcortexapp.com"
    return api_url.replace("://api.", "://app.")


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


def _read_catalog_tag(content: str) -> str | None:
    """Extract x-cortex-tag from a catalog YAML file."""
    try:
        data = yaml.safe_load(content)
        return data.get("info", {}).get("x-cortex-tag") if isinstance(data, dict) else None
    except Exception:
        return None


def _read_resource_tag(content: str, kind: str) -> str | None:
    """Extract tag/type identifier from a JSON or YAML resource file."""
    try:
        data = yaml.safe_load(content)
        if not isinstance(data, dict):
            data = json.loads(content)
        return data.get("type") if kind == "entity-types" else data.get("tag")
    except Exception:
        return None


def _collect_solution_resources(path: Path) -> dict[str, list[str]]:
    """Return {kind: [tag, ...]} for all deletable resources in a solution directory."""
    resources: dict[str, list[str]] = {
        "entity-types": [],
        "entity-relationship-types": [],
        "catalog": [],
        "scorecards": [],
        "workflows": [],
    }
    for kind in resources:
        subdir = path / kind
        if not subdir.exists() or not subdir.is_dir():
            continue
        for f in sorted(subdir.iterdir()):
            if not f.is_file() or f.suffix not in (".json", ".yaml", ".yml"):
                continue
            try:
                content = f.read_text(encoding="utf-8")
                tag = (
                    _read_catalog_tag(content)
                    if kind == "catalog"
                    else _read_resource_tag(content, kind)
                )
                if tag:
                    resources[kind].append(tag)
            except Exception:
                pass
    return resources


def _delete_parallel(client, tags: list[str], endpoint_fn) -> tuple[int, int]:
    """Delete resources in parallel. Returns (removed, failed) counts."""
    deleted = failed = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_tag = {
            executor.submit(client.delete, endpoint_fn(tag)): tag for tag in tags
        }
        for future in as_completed(future_to_tag):
            tag = future_to_tag[future]
            try:
                future.result()
                typer.echo(f"   Deleted: {tag}")
                deleted += 1
            except Exception as e:
                err = str(e)
                if "404" in err or "Not Found" in err:
                    typer.echo(f"   Not found (skipped): {tag}")
                    deleted += 1
                else:
                    typer.echo(f"   Failed: {tag} — {err}")
                    failed += 1
    return deleted, failed


def _run_uninstall(client, path: Path, yes: bool) -> None:
    """Collect resources, confirm, then delete in reverse import order."""
    resources = _collect_solution_resources(path)
    total = sum(len(v) for v in resources.values())

    if total == 0:
        typer.echo("No resources found to remove.")
        return

    typer.echo("\nThis will remove the following resources:")
    for kind in ("workflows", "scorecards", "catalog", "entity-relationship-types", "entity-types"):
        count = len(resources[kind])
        if count:
            typer.echo(f"  {kind}: {count}")
    typer.echo()

    if not yes:
        confirmed = typer.confirm("Proceed with uninstall?", default=False)
        if not confirmed:
            typer.echo("Aborted.")
            raise typer.Exit(0)

    # Delete in reverse import order
    steps = [
        ("workflows",                 lambda t: f"api/v1/workflows/{t}"),
        ("scorecards",                lambda t: f"api/v1/scorecards/{t}"),
        ("catalog",                   lambda t: f"api/v1/catalog/{t}"),
        ("entity-relationship-types", lambda t: f"api/v1/relationship-types/{t}"),
        ("entity-types",              lambda t: f"api/v1/catalog/definitions/{t}"),
    ]

    stats: dict[str, tuple[int, int]] = {}
    for kind, endpoint_fn in steps:
        tags = resources[kind]
        if not tags:
            continue
        typer.echo(f"\nRemoving {kind}...")
        deleted, failed = _delete_parallel(client, tags, endpoint_fn)
        stats[kind] = (deleted, failed)

    total_removed = sum(d for d, _ in stats.values())
    total_failed = sum(f for _, f in stats.values())

    width = 80
    typer.echo(f"\n{'=' * width}")
    typer.echo("UNINSTALL SUMMARY")
    typer.echo(f"{'=' * width}\n")
    for kind, (d, f) in stats.items():
        if d + f > 0:
            typer.echo(f"{kind}:")
            typer.echo(f"  Removed: {d}")
            if f:
                typer.echo(f"  Failed:  {f}")
    typer.echo(f"\nTOTAL: {total_removed} removed, {total_failed} failed\n")
    typer.echo("=" * width)


@app.command("list")
def list_solutions(ctx: typer.Context):
    """List all available solutions."""
    solutions_dir = ctx.obj.get("solutions_dir") if ctx.obj else None
    tags = _list_solution_tags(solutions_dir)
    table = Table(title="Available Solutions")
    table.add_column("Tag", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Description")
    for tag in tags:
        readme = _get_readme(tag, solutions_dir)
        if readme is None:
            continue
        fm = _parse_frontmatter(readme)
        table.add_row(tag, fm.get("name", tag), fm.get("description", ""))
    console.print(table)


def _print_readme(text: str, plain: bool = False) -> None:
    """Render README with left-justified headings and Rich Markdown body blocks.

    When plain=True, markdown structure is preserved (bold, code blocks, etc.)
    but all color is removed — suitable for light-mode terminals.
    """
    # Strip YAML frontmatter
    body = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL).strip()

    out = Console(no_color=True) if plain else console

    heading_styles = {"# ": "bold", "## ": "bold underline", "### ": "bold"}
    pending: list[str] = []
    in_code_block = False

    def flush() -> None:
        block = "\n".join(pending).strip()
        if block:
            out.print(Markdown(block))
        pending.clear()

    for line in body.split("\n"):
        if line.startswith("```"):
            if not in_code_block:
                flush()
            in_code_block = not in_code_block
            continue

        if in_code_block:
            out.print(f"  [cyan]{line}[/cyan]" if line else "")
            continue

        for prefix, style in heading_styles.items():
            if line.startswith(prefix):
                flush()
                out.print(f"\n[{style}]{line[len(prefix):]}[/{style}]")
                break
        else:
            pending.append(line)

    flush()


def _osc8(url: str, text: str) -> str:
    """Wrap text in an OSC 8 terminal hyperlink."""
    return f"\033]8;;{url}\033\\{text}\033]8;;\033\\"


def _show_diagram(readme: str, entity_tags: set[str] | None = None, ui_url: str = "https://app.getcortexapp.com") -> None:
    block = _extract_first_codeblock(readme)
    if not block:
        return
    console.print()
    for line in block.split("\n"):
        if entity_tags:
            # Replace longest matches first to avoid partial-tag substitutions
            for tag in sorted(entity_tags, key=len, reverse=True):
                if tag in line:
                    line = line.replace(tag, _osc8(f"{ui_url}/admin?tag={tag}", tag))
        console.print(f"  {line}", highlight=False, markup=False)


def _show_next_steps(readme: str) -> None:
    section = _extract_section(readme, "After Installing")
    if section:
        console.print()
        console.print(Markdown(section))


def _post_install_menu(
    readme: str,
    import_report: str = "",
    entity_tags: set[str] | None = None,
    ui_url: str = "https://app.getcortexapp.com",
) -> None:
    options = [
        ("1", "Project diagram"),
        ("2", "Next steps"),
        ("3", "Full README"),
        ("4", "Import report"),
        ("5", "Exit"),
    ]
    actions = {
        "1": lambda: _show_diagram(readme, entity_tags=entity_tags, ui_url=ui_url),
        "2": lambda: _show_next_steps(readme),
        "3": lambda: (console.print(), _print_readme(readme)),
        "4": lambda: (console.print(), typer.echo(import_report)),
    }

    while True:
        console.print()
        console.print(Rule(" What next? ", style="bold"))
        for key, label in options:
            console.print(f"  [cyan]{key}[/cyan]  {label}")
        console.print()

        choice = Prompt.ask("Choice", choices=[k for k, _ in options], show_choices=False)

        if choice == "5":
            break
        actions[choice]()


@app.command()
def info(
    ctx: typer.Context,
    solution: str = typer.Option(..., "--solution", "-s", help="Solution tag"),
    plain: bool = typer.Option(False, "--plain", help="Render README in plain black text (no colors)."),
):
    """Show README for a solution."""
    solutions_dir = ctx.obj.get("solutions_dir") if ctx.obj else None
    readme = _get_readme(solution, solutions_dir)
    if readme is None:
        avail = ", ".join(_list_solution_tags(solutions_dir))
        typer.echo(f"Error: Solution '{solution}' not found. Available: {avail}")
        raise typer.Exit(1)
    _print_readme(readme, plain=plain)


@app.command()
def install(
    ctx: typer.Context,
    solution: str = typer.Option(..., "--solution", "-s", help="Solution tag"),
    no_prompt: bool = typer.Option(False, "--no-prompt", help="Skip the post-install interactive menu"),
):
    """Install a solution into the current Cortex workspace."""
    solutions_dir = ctx.obj.get("solutions_dir") if ctx.obj else None
    if solution not in _list_solution_tags(solutions_dir):
        avail = ", ".join(_list_solution_tags(solutions_dir))
        typer.echo(f"Error: Solution '{solution}' not found. Available: {avail}")
        raise typer.Exit(1)

    ctx.obj["client"] = _build_client(ctx)

    import cortexapps_cli.commands.backup as backup

    root = _solutions_root(solutions_dir)
    typer.echo(f"\nInstalling {solution}...")
    if _TTY_SUPPORT and sys.stdin.isatty():
        console.print("  [dim]Ctrl+o to show/hide import details[/dim]")

    def _do_import() -> None:
        if solutions_dir:
            backup.import_tenant(ctx, directory=str(root / solution), force=False)
        else:
            with as_file(root / solution) as solution_path:
                backup.import_tenant(ctx, directory=str(solution_path), force=False)

    output = _run_import_with_toggle(_do_import)
    total_match = re.search(r"TOTAL: (\d+) imported, (\d+) failed", output)
    if total_match:
        total_imported = int(total_match.group(1))
        total_failed = int(total_match.group(2))
        if total_failed:
            failed_m = re.search(r"={20,}\nFAILED IMPORTS.*", output, re.DOTALL)
            if failed_m:
                typer.echo(failed_m.group(0))
            typer.echo(f"\n  {total_imported} imported, {total_failed} failed")
        else:
            typer.echo(f"  {total_imported} resources imported")
    else:
        typer.echo(output)

    if not no_prompt:
        readme = _get_readme(solution, solutions_dir)
        if readme:
            entity_tags: set[str] = set()
            ui_url = _get_ui_url(ctx)
            try:
                if solutions_dir:
                    resources = _collect_solution_resources(root / solution)
                else:
                    with as_file(root / solution) as sp:
                        resources = _collect_solution_resources(sp)
                entity_tags = set(resources.get("catalog", []))
            except Exception:
                pass
            _post_install_menu(readme, import_report=output, entity_tags=entity_tags, ui_url=ui_url)


@app.command()
def uninstall(
    ctx: typer.Context,
    solution: str = typer.Option(..., "--solution", "-s", help="Solution tag"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """Remove all entities installed by a solution from the current Cortex workspace."""
    solutions_dir = ctx.obj.get("solutions_dir") if ctx.obj else None
    if solution not in _list_solution_tags(solutions_dir):
        avail = ", ".join(_list_solution_tags(solutions_dir))
        typer.echo(f"Error: Solution '{solution}' not found. Available: {avail}")
        raise typer.Exit(1)

    ctx.obj["client"] = _build_client(ctx)
    client = ctx.obj["client"]

    root = _solutions_root(solutions_dir)
    if solutions_dir:
        _run_uninstall(client, root / solution, yes)
    else:
        with as_file(root / solution) as solution_path:
            _run_uninstall(client, solution_path, yes)
