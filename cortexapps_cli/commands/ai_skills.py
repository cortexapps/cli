import json
import re
from pathlib import Path
from typing import Optional

import typer
import yaml
from typing_extensions import Annotated

app = typer.Typer(help="AI Skills commands", no_args_is_help=True)


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Split a SKILL.md file into its YAML frontmatter and body."""
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
    if not match:
        return {}, content
    try:
        frontmatter = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        frontmatter = {}
    return frontmatter, match.group(2)


def _local_links(text: str, base_dir: Path) -> list[Path]:
    """Return local files referenced by markdown links in text, resolved against base_dir."""
    links = []
    for target in re.findall(r"\]\(([^)]+)\)", text):
        target = target.split("#")[0].strip()
        if not target or target.startswith(("http://", "https://", "${")):
            continue
        candidate = (base_dir / target).resolve()
        if candidate.is_file():
            links.append(candidate)
    return links


def _has_deep_references(skill_dir: Path, body: str) -> bool:
    """True if a file SKILL.md links to itself links to another local file (>1 level deep)."""
    for linked in _local_links(body, skill_dir):
        try:
            linked_body = linked.read_text(encoding="utf-8")
        except OSError:
            continue
        if _local_links(linked_body, linked.parent):
            return True
    return False


def _entity_yaml(tag: str, entity_type: str, description: str, relationships: list) -> str:
    info = {
        "title": tag,
        "description": description or "",
        "x-cortex-tag": tag,
        "x-cortex-type": entity_type,
        "x-cortex-definition": {},
    }
    if relationships:
        info["x-cortex-relationships"] = relationships
    doc = {"openapi": "3.0.0", "info": info}
    return yaml.safe_dump(doc, sort_keys=False)


def _push_entity(client, entity_yaml: str) -> None:
    client.post(
        "api/v1/open-api",
        data=entity_yaml,
        content_type="application/openapi;charset=UTF-8",
    )


def _push_custom_data(client, tag: str, key: str, value) -> None:
    client.post(
        f"api/v1/catalog/{tag}/custom-data",
        data={"key": key, "value": str(value)},
        params={"force": False},
    )


@app.command()
def sync(
    ctx: typer.Context,
    directory: Annotated[
        Path,
        typer.Option(
            "--directory", "-d",
            help="Directory containing plugin folders, each with .claude-plugin/plugin.json and skills/*/SKILL.md (the eng-commons layout).",
        ),
    ],
    service: Annotated[
        Optional[str],
        typer.Option(
            "--service", "-s",
            help="Cortex Service tag to link every synced plugin/skill's ownership to (ai-plugin-service / ai-skill-service).",
            show_default=False,
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", "-n", help="Print what would be synced without pushing anything to Cortex."),
    ] = False,
):
    """
    Scan a plugins directory and sync ai-plugin / ai-skill catalog entities into Cortex.

    Expects the eng-commons layout:

        <directory>/<plugin>/.claude-plugin/plugin.json
        <directory>/<plugin>/skills/<skill>/SKILL.md

    For each skill, also pushes the lineCount, descriptionCharCount, and
    hasDeepReferences Custom Data keys the ai-skills-quality scorecard reads
    (see cortexapps_cli/solutions/ai-skills/scorecards/ai-skills-quality.yaml),
    via the Custom Data API.

    Re-run this on a schedule tied to when skills actually change (a GitHub
    Action or webhook on push to the plugins repo), not on a fixed timer —
    these values change maybe a couple of times a year, so recomputing them
    multiple times a day is wasted work the scorecard evaluator would
    otherwise have to redo live against git on every single evaluation.
    """
    client = None if dry_run else ctx.obj["client"]

    plugin_dirs = sorted(
        p for p in directory.iterdir()
        if p.is_dir() and (p / ".claude-plugin" / "plugin.json").is_file()
    )
    if not plugin_dirs:
        typer.echo(f"No plugins found under {directory} (expected <plugin>/.claude-plugin/plugin.json)")
        raise typer.Exit(1)

    synced_plugins = 0
    synced_skills = 0

    for plugin_dir in plugin_dirs:
        manifest = json.loads((plugin_dir / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        plugin_tag = manifest.get("name", plugin_dir.name)
        plugin_description = manifest.get("description", "")

        skill_tags = []
        skills_dir = plugin_dir / "skills"
        if skills_dir.is_dir():
            for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
                skill_md = skill_dir / "SKILL.md"
                if not skill_md.is_file():
                    continue

                content = skill_md.read_text(encoding="utf-8")
                frontmatter, body = _parse_frontmatter(content)
                skill_tag = frontmatter.get("name", skill_dir.name)
                skill_description = frontmatter.get("description", "")

                line_count = len(body.strip("\n").split("\n")) if body.strip("\n") else 0
                description_char_count = len(skill_description)
                has_deep_references = _has_deep_references(skill_dir, body)

                relationships = []
                if service:
                    relationships.append({"type": "ai-skill-service", "destinations": [{"tag": service}]})

                skill_yaml = _entity_yaml(skill_tag, "ai-skill", skill_description, relationships)

                if dry_run:
                    typer.echo(f"--- {skill_tag} (ai-skill) ---")
                    typer.echo(skill_yaml)
                    typer.echo(
                        f"  custom-data: lineCount={line_count} "
                        f"descriptionCharCount={description_char_count} "
                        f"hasDeepReferences={has_deep_references}"
                    )
                else:
                    _push_entity(client, skill_yaml)
                    _push_custom_data(client, skill_tag, "lineCount", line_count)
                    _push_custom_data(client, skill_tag, "descriptionCharCount", description_char_count)
                    _push_custom_data(client, skill_tag, "hasDeepReferences", "true" if has_deep_references else "false")

                skill_tags.append(skill_tag)
                synced_skills += 1

        relationships = []
        if skill_tags:
            relationships.append({
                "type": "ai-plugin-skills",
                "destinations": [{"tag": t} for t in skill_tags],
            })
        if service:
            relationships.append({"type": "ai-plugin-service", "destinations": [{"tag": service}]})

        plugin_yaml = _entity_yaml(plugin_tag, "ai-plugin", plugin_description, relationships)

        if dry_run:
            typer.echo(f"--- {plugin_tag} (ai-plugin) ---")
            typer.echo(plugin_yaml)
        else:
            _push_entity(client, plugin_yaml)

        synced_plugins += 1

    suffix = " (dry run — nothing was pushed)" if dry_run else ""
    typer.echo(f"\nSynced {synced_plugins} plugin(s), {synced_skills} skill(s){suffix}.")
