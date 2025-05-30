from datetime import datetime
from typing import Optional
from typing import List
from typing_extensions import Annotated
import typer
import json
import os
from rich import print, print_json
from rich.console import Console
from enum import Enum
import yaml

import cortexapps_cli.commands.scorecards as scorecards
import cortexapps_cli.commands.catalog as catalog
import cortexapps_cli.commands.entity_types as entity_types
import cortexapps_cli.commands.ip_allowlist as ip_allowlist
import cortexapps_cli.commands.plugins as plugins
import cortexapps_cli.commands.workflows as workflows


app = typer.Typer(help="Backup commands")

# Need to support the following:
# DONE -> Catalog
# Custom Data from API
# Custom Events
# Custom Metrics
# Dependencies from API
# Deploys from API
# Docs
# Eng Intel - User Labels
# DONE -> Entity Types
# Groups from API -> would have to loop over all entities
# DONE -> IP Allowlist
# Packages from API -> would have to loop over all entities
# DONE -> Plugins
# DONE -> Scorecards
# Secrets
# DONE -> Workflows

def _create_directory(directory):
    if not os.path.isdir(directory):
        os.mkdir(directory, 0o700)

def _directory_name(directory, backup_type):
    directory = directory + "/" + backup_type
    _create_directory(directory)
    print("Getting " + backup_type)
    return directory

def _file_name(directory, tag, content, extension):
    print("--> " + tag)
    file = directory + "/" + tag + "." + extension
    if extension == "json":
        is_json = True
    else:
        is_json = False
    _write_file(content, file, is_json)

def _write_file(content, file, is_json=False):
    with open(file, 'w') as f:
        if is_json:
            # plugins return a dict?

            #json_data = json.loads(str(content).replace("'", '"'))  # Fixing single quotes to double quotes for JSON format

            #json_data = json.loads(content)
            #json.dump(json_data, f, indent=4)

            #print_json(json_data, file=f)
            #print(json.dumps(json_data, indent=4), file=f)

            #print_json(data=content, file=f)
            print(content, file=f)

            #json.dump(content, f, indent=4)
            #console.print_json(content)
            #console = Console(record=True)
            #console.print_json(data=content)
            #f.write(console.export_text())
            #f.write(data)
        else:
            f.write(str(content) + "\n")
    f.close()

def _catalog(ctx, directory, catalog_types):
    directory = _directory_name(directory, "catalog")

    data = catalog.list_descriptors(ctx, types=catalog_types, page_size=1000, yaml="true", _print=False)

    for descriptor in data['descriptors']:
       try:
           y = yaml.safe_load(str(descriptor))
           tag = y['info']['x-cortex-tag']
           y = yaml.dump(y, default_flow_style=False)
       except:
           print("error")
           print(str(descriptor))
           continue
       finally:
           # Slash will be interpreted as a sub-directory
           tag = tag.replace("/", "-")
           _file_name(directory, tag, y, "yaml")

def _entity_types(ctx, directory):
    directory = _directory_name(directory, "entity-types")

    data = entity_types.list(ctx, include_built_in=False, page=0, page_size=250, _print=False)
    definitions_sorted = sorted(data['definitions'], key=lambda x: x["type"])

    for definition in definitions_sorted:
        tag = definition['type']
        json_string = json.dumps(definition, indent=4)
        _file_name(directory, tag, json_string, "json")

def _ip_allowlist(ctx, directory):
    directory = _directory_name(directory, "ip-allowlist")
    #file = directory + "/ip-allowlist.json"

    content = ip_allowlist.get(ctx, page=None, page_size=None, _print=False)
    _file_name(directory, "ip-allowlist", str(content), "json") 

def _plugins(ctx, directory):
    directory = _directory_name(directory, "plugins")

    list = plugins.list(ctx, _print=False, include_drafts="true", page=None, page_size=None)
    tags = [plugin["tag"] for plugin in list["plugins"]]
    tags_sorted = sorted(tags)
    for tag in tags_sorted:
        content = plugins.get(ctx, tag_or_id=tag, include_blob="true", _print=False)
        _file_name(directory, tag, content, "json")

def _scorecards(ctx, directory):
    directory = _directory_name(directory, "scorecards")

    list = scorecards.list(ctx, show_drafts=True, page=None, page_size=None, _print=False)
    tags = [scorecard["tag"] for scorecard in list["scorecards"]]
    tags_sorted = sorted(tags)
    for tag in tags_sorted:
        content = scorecards.descriptor(ctx, scorecard_tag=tag, _print=False)
        _file_name(directory, tag, content, "yaml")

def _workflows(ctx, directory):
    directory = _directory_name(directory, "workflows")

    list = workflows.list(ctx, _print=False, include_actions="false", page=None, page_size=None, search_query=None)
    tags = [workflow["tag"] for workflow in list["workflows"]]
    tags_sorted = sorted(tags)
    for tag in tags_sorted:
        try:
            content = workflows.get(ctx, tag=tag, yaml="true", _print=False)
            _file_name(directory, tag, content, "yaml")
        except:
            print("failed for " + tag)

backupTypes = {
        "catalog",
        "entity-types",
        "ip-allowlist",
        "plugins",
        "scorecards",
        "workflows"
}
backupString = ','.join(backupTypes) 

def _parse_export_types(value: str) -> List[str]:
    if value == "all":
        return backupTypes
    types = []
    for val in value:
        for item in val.split(","):
            if item not in backupTypes:
               raise typer.BadParameter(item + "  is not a valid type. Valid types are: " + backupString + ".")
            else:
               types.append(item)
    return types

def _parse_catalog_types(ctx, catalog_types):
    data = entity_types.list(ctx, include_built_in=True, page=0, page_size=250, _print=False)

    built_in = ['service', 'team', 'domain']
    tags = [entity_type["type"] for entity_type in data["definitions"]]
    tags_sorted = sorted(tags + built_in)
    all_types_string = ','.join(tags_sorted) 
    if catalog_types == "all":
        return all_types_string

    for item in catalog_types.split(","):
        if item not in tags_sorted:
           raise typer.BadParameter(item + "  is not a valid type. Valid types are: " + all_types_string  + ".")
    return catalog_types

@app.command()
def export(
    ctx: typer.Context,
    export_types: List[str] = typer.Option(_parse_export_types("all"), "--export-types", "-e", help="some help test", callback=_parse_export_types),
    catalog_types: str = typer.Option("all", "--catalog-types", "-c", help="Comma separated list of catalog types to export, defaults to all"),
    directory: str = typer.Option(os.path.expanduser('~') + '/.cortex/export/' + datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), "--directory", "-d", help="Location of export directory, defaults to ~/.cortex/export/<date>-tenant"),
):
    """
    Export tenant


    """
    export_types = sorted(list(set(export_types)))

    client = ctx.obj["client"]
    catalog_types = _parse_catalog_types(ctx, catalog_types)
    directory = directory + "-" + client.tenant
    _create_directory(directory)
    if "catalog" in export_types:
        _catalog(ctx, directory, catalog_types)
    if "entity-types" in export_types:
        _entity_types(ctx, directory)
    if "ip-allowlist" in export_types:
        _ip_allowlist(ctx, directory)
    if "plugins" in export_types:
        _plugins(ctx, directory)
    if "scorecards" in export_types:
        _scorecards(ctx, directory)
    if "workflows" in export_types:
        _workflows(ctx, directory)

    print("\nExport complete!")
    print("Contents available in " + directory)

def _import_ip_allowlist(directory):
    if os.path.isdir(directory):
        print("Processing: " + directory)
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                print("   Importing: " + filename)
                ip_allowlist.get(ctx, file=file_path, force=False, _print=False)

def _import_entity_types(directory):
    if os.path.isdir(directory):
        print("FOUND: " + directory)

def _import_catalog(directory):
    if os.path.isdir(directory):
        print("FOUND: " + directory)

def _import_plugins(directory):
    if os.path.isdir(directory):
        print("FOUND: " + directory)

def _import_scorecards(directory):
    if os.path.isdir(directory):
        print("FOUND: " + directory)

def _import_workflows(directory):
    if os.path.isdir(directory):
        print("FOUND: " + directory)

@app.command("import")
def import_tenant(
    ctx: typer.Context,
    directory: str = typer.Option(..., "--directory", "-d", help="Location of import directory."),
):
    """
    Import data into tenant

    """
    client = ctx.obj["client"]

    print("import directory = " + directory)
    _import_ip_allowlist(directory + "/ip-allowlist")
    _import_entity_types(directory + "/entity-types")
    _import_catalog(directory + "/catalog")
    _import_plugins(directory + "/plugins")
    _import_scorecards(directory + "/scorecards")
    _import_workflows(directory + "/workflows")

