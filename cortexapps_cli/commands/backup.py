from datetime import datetime
from typing import Optional
from typing import List
from typing_extensions import Annotated
import typer
import json
import os
import tempfile
import sys
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from rich import print, print_json
from rich.console import Console
from enum import Enum
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed

import cortexapps_cli.commands.scorecards as scorecards
import cortexapps_cli.commands.catalog as catalog
import cortexapps_cli.commands.entity_types as entity_types
import cortexapps_cli.commands.entity_relationship_types as entity_relationship_types
import cortexapps_cli.commands.entity_relationships as entity_relationships
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
            json.dump(content, f, indent=2)
        else:
            f.write(str(content) + "\n")
    f.close()

def _export_catalog(ctx, directory, catalog_types):
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

def _export_entity_types(ctx, directory):
    directory = _directory_name(directory, "entity-types")

    data = entity_types.list(ctx, include_built_in=False, page=0, page_size=250, _print=False)
    definitions_sorted = sorted(data['definitions'], key=lambda x: x["type"])

    for definition in definitions_sorted:
        tag = definition['type']
        _file_name(directory, tag, definition, "json")

def _export_ip_allowlist(ctx, directory):
    directory = _directory_name(directory, "ip-allowlist")
    file = directory + "/ip-allowlist.json"

    content = ip_allowlist.get(ctx, page=None, page_size=None, _print=False)
    _file_name(directory, "ip-allowlist", content, "json")

def _export_entity_relationship_types(ctx, directory):
    directory = _directory_name(directory, "entity-relationship-types")

    data = entity_relationship_types.list(ctx, page=None, page_size=250, _print=False)
    relationship_types_sorted = sorted(data['relationshipTypes'], key=lambda x: x["tag"])

    for rel_type in relationship_types_sorted:
        tag = rel_type['tag']
        _file_name(directory, tag, rel_type, "json")

def _export_entity_relationships(ctx, directory):
    directory = _directory_name(directory, "entity-relationships")

    # First get all relationship types
    rel_types_data = entity_relationship_types.list(ctx, page=None, page_size=250, _print=False)
    rel_types = [rt['tag'] for rt in rel_types_data['relationshipTypes']]

    # For each relationship type, export all relationships
    for rel_type in sorted(rel_types):
        data = entity_relationships.list(ctx, relationship_type=rel_type, page=None, page_size=250, _print=False)
        relationships = data.get('relationships', [])

        if relationships:
            _file_name(directory, rel_type, relationships, "json")

def _export_plugins(ctx, directory):
    directory = _directory_name(directory, "plugins")

    list = plugins.list(ctx, _print=False, include_drafts="true", page=None, page_size=None)
    tags = [plugin["tag"] for plugin in list["plugins"]]
    tags_sorted = sorted(tags)

    def fetch_plugin(tag):
        try:
            content = plugins.get(ctx, tag_or_id=tag, include_blob="true", _print=False)
            return (tag, content, None)
        except Exception as e:
            return (tag, None, str(e))

    # Fetch all plugins in parallel
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(fetch_plugin, tag): tag for tag in tags_sorted}
        results = []
        for future in as_completed(futures):
            results.append(future.result())

    # Sort results alphabetically and write in order
    for tag, content, error in sorted(results, key=lambda x: x[0]):
        if error:
            print(f"Failed to export plugin {tag}: {error}")
        else:
            _file_name(directory, tag, content, "json")

def _export_scorecards(ctx, directory):
    directory = _directory_name(directory, "scorecards")

    list = scorecards.list(ctx, show_drafts=True, page=None, page_size=None, _print=False)
    tags = [scorecard["tag"] for scorecard in list["scorecards"]]
    tags_sorted = sorted(tags)

    def fetch_scorecard(tag):
        try:
            content = scorecards.descriptor(ctx, scorecard_tag=tag, _print=False)
            return (tag, content, None)
        except Exception as e:
            return (tag, None, str(e))

    # Fetch all scorecards in parallel
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(fetch_scorecard, tag): tag for tag in tags_sorted}
        results = []
        for future in as_completed(futures):
            results.append(future.result())

    # Sort results alphabetically and write in order
    for tag, content, error in sorted(results, key=lambda x: x[0]):
        if error:
            print(f"Failed to export scorecard {tag}: {error}")
        else:
            _file_name(directory, tag, content, "yaml")

def _export_workflows(ctx, directory):
    directory = _directory_name(directory, "workflows")

    # Get all workflows with actions in one API call
    list = workflows.list(ctx, _print=False, include_actions="true", page=None, page_size=None, search_query=None)
    workflows_data = sorted(list["workflows"], key=lambda x: x["tag"])

    # Convert JSON workflows to YAML and write them
    for workflow in workflows_data:
        tag = workflow["tag"]
        try:
            # Convert the JSON workflow data to YAML format
            workflow_yaml = yaml.dump(workflow, default_flow_style=False, sort_keys=False)
            _file_name(directory, tag, workflow_yaml, "yaml")
        except Exception as e:
            print(f"Failed to export workflow {tag}: {e}")

backupTypes = {
        "catalog",
        "entity-types",
        "entity-relationship-types",
        "entity-relationships",
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
               raise typer.BadParameter(item + " is not a valid type. Valid types are: " + backupString + ".")
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
    catalog_types: str = typer.Option("all", "--catalog-types", "-c", help="Comma separated list of catalog types to export, defaults to service,team,domain plus all user-created entity-types"),
    directory: str = typer.Option(os.path.expanduser('~') + '/.cortex/export/' + datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), "--directory", "-d", help="Location of export directory, defaults to ~/.cortex/export/<date>-tenant"),
):
    """
    Export tenant

    Exports the following objects:
    - catalog
    - entity-types
    - entity-relationship-types
    - entity-relationships
    - ip-allowlist
    - plugins
    - scorecards
    - workflows

    By default, it does not export any entities that would be created by an integration, for example AWS objects.  This is because these
    entities are maintained by the integration and do not need to be backed up.

    However, these entities can be export by referencing them in the catalog-types parameter, for example this command
    would export all AWS S3 buckets::

    cortex backup export --export-types catalog --catalog-types AWS::S3::Bucket

    It does not back up everything in the tenant.  For example these objects are not backed up:
    - api-keys
    - custom-events
    - custom-metadata created by the public API
    - custom-metrics
    - dependencies created by the API
    - deploys
    - docs created by the API
    - groups added by the API
    - packages
    - secrets

    In general, if there is a bulk export API method for a Cortex object, it will be included in the export.
    """

    export_types = sorted(list(set(export_types)))

    client = ctx.obj["client"]
    catalog_types = _parse_catalog_types(ctx, catalog_types)
    directory = directory + "-" + client.tenant
    _create_directory(directory)
    if "catalog" in export_types:
        _export_catalog(ctx, directory, catalog_types)
    if "entity-types" in export_types:
        _export_entity_types(ctx, directory)
    if "entity-relationship-types" in export_types:
        _export_entity_relationship_types(ctx, directory)
    if "entity-relationships" in export_types:
        _export_entity_relationships(ctx, directory)
    if "ip-allowlist" in export_types:
        _export_ip_allowlist(ctx, directory)
    if "plugins" in export_types:
        _export_plugins(ctx, directory)
    if "scorecards" in export_types:
        _export_scorecards(ctx, directory)
    if "workflows" in export_types:
        _export_workflows(ctx, directory)

    print("\nExport complete!")
    print("Contents available in " + directory)

def _import_ip_allowlist(ctx, directory):
    imported = 0
    failed = []
    if os.path.isdir(directory):
        print("Processing: " + directory)
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                try:
                    print("   Importing: " + filename)
                    ip_allowlist.replace(ctx, file_input=open(file_path), addresses=None, force=False, _print=False)
                    imported += 1
                except Exception as e:
                    print(f"   Failed to import {filename}: {type(e).__name__} - {str(e)}")
                    failed.append((file_path, type(e).__name__, str(e)))
    return ("ip-allowlist", imported, failed)

def _import_entity_types(ctx, force, directory):
    imported = 0
    failed = []
    if os.path.isdir(directory):
        print("Processing: " + directory)
        for filename in sorted(os.listdir(directory)):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                try:
                    print("   Importing: " + filename)
                    entity_types.create(ctx, file_input=open(file_path), force=force)
                    imported += 1
                except Exception as e:
                    print(f"   Failed to import {filename}: {type(e).__name__} - {str(e)}")
                    failed.append((file_path, type(e).__name__, str(e)))
    return ("entity-types", imported, failed)

def _import_entity_relationship_types(ctx, directory):
    results = []
    failed_count = 0

    if os.path.isdir(directory):
        print("Processing: " + directory)

        # Get list of existing relationship types
        existing_rel_types_data = entity_relationship_types.list(ctx, page=None, page_size=250, _print=False)
        existing_tags = {rt['tag'] for rt in existing_rel_types_data.get('relationshipTypes', [])}

        files = [(filename, os.path.join(directory, filename))
                 for filename in sorted(os.listdir(directory))
                 if os.path.isfile(os.path.join(directory, filename))]

        def import_rel_type_file(file_info):
            filename, file_path = file_info
            tag = filename.replace('.json', '')
            try:
                # Check if relationship type already exists
                if tag in existing_tags:
                    # Update existing relationship type
                    entity_relationship_types.update(ctx, tag=tag, file_input=open(file_path), _print=False)
                else:
                    # Create new relationship type
                    entity_relationship_types.create(ctx, file_input=open(file_path), _print=False)
                return (tag, file_path, None, None)
            except typer.Exit as e:
                return (tag, file_path, "HTTP", "Validation or HTTP error")
            except Exception as e:
                return (tag, file_path, type(e).__name__, str(e))

        # Import all files in parallel
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = {executor.submit(import_rel_type_file, file_info): file_info[0] for file_info in files}
            results = []
            for future in as_completed(futures):
                results.append(future.result())

        # Print results in alphabetical order
        failed_count = 0
        for tag, file_path, error_type, error_msg in sorted(results, key=lambda x: x[0]):
            if error_type:
                print(f"   Failed to import {tag}: {error_type} - {error_msg}")
                failed_count += 1
            else:
                print(f"   Importing: {tag}")

        if failed_count > 0:
            print(f"\n   Total entity relationship type import failures: {failed_count}")

    return ("entity-relationship-types", len(results) - failed_count, [(fp, et, em) for tag, fp, et, em in results if et])

def _import_entity_relationships(ctx, directory):
    results = []
    failed_count = 0

    if os.path.isdir(directory):
        print("Processing: " + directory)

        files = [(filename, os.path.join(directory, filename))
                 for filename in sorted(os.listdir(directory))
                 if os.path.isfile(os.path.join(directory, filename))]

        def import_relationships_file(file_info):
            filename, file_path = file_info
            rel_type = filename.replace('.json', '')
            try:
                # Read the relationships file
                with open(file_path) as f:
                    relationships = json.load(f)

                # Convert list format to the format expected by update-bulk
                # The export saves the raw relationships list, but update-bulk needs {"relationships": [...]}
                if isinstance(relationships, list):
                    data = {"relationships": []}
                    for rel in relationships:
                        # Extract source and destination tags from sourceEntity and destinationEntity
                        source_tag = rel.get("sourceEntity", {}).get("tag")
                        dest_tag = rel.get("destinationEntity", {}).get("tag")
                        data["relationships"].append({
                            "source": source_tag,
                            "destination": dest_tag
                        })

                    # Use update-bulk to replace all relationships for this type
                    # Create a temporary file to pass the data
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                        json.dump(data, temp_file)
                        temp_file_name = temp_file.name

                    try:
                        entity_relationships.update_bulk(ctx, relationship_type=rel_type, file_input=open(temp_file_name), force=True, _print=False)
                    finally:
                        os.unlink(temp_file_name)

                return (rel_type, file_path, None, None)
            except typer.Exit as e:
                return (rel_type, file_path, "HTTP", "Validation or HTTP error")
            except Exception as e:
                return (rel_type, file_path, type(e).__name__, str(e))

        # Import all files in parallel
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = {executor.submit(import_relationships_file, file_info): file_info[0] for file_info in files}
            results = []
            for future in as_completed(futures):
                results.append(future.result())

        # Print results in alphabetical order
        failed_count = 0
        for rel_type, file_path, error_type, error_msg in sorted(results, key=lambda x: x[0]):
            if error_type:
                print(f"   Failed to import {rel_type}: {error_type} - {error_msg}")
                failed_count += 1
            else:
                print(f"   Importing: {rel_type}")

        if failed_count > 0:
            print(f"\n   Total entity relationship import failures: {failed_count}")

    return ("entity-relationships", len(results) - failed_count, [(fp, et, em) for rt, fp, et, em in results if et])

def _import_catalog(ctx, directory):
    results = []
    failed_count = 0
    if os.path.isdir(directory):
        print("Processing: " + directory)
        files = [(filename, os.path.join(directory, filename))
                 for filename in sorted(os.listdir(directory))
                 if os.path.isfile(os.path.join(directory, filename))]

        def import_catalog_file(file_info):
            filename, file_path = file_info
            print(f"   Importing: {filename}")
            try:
                with open(file_path) as f:
                    catalog.create(ctx, file_input=f, _print=False)
                return (filename, file_path, None, None)
            except typer.Exit as e:
                # typer.Exit is raised by the HTTP client on errors
                return (filename, file_path, "HTTP", "Validation or HTTP error")
            except Exception as e:
                return (filename, file_path, type(e).__name__, str(e))

        # Import all files in parallel
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = {executor.submit(import_catalog_file, file_info): file_info[0] for file_info in files}
            results = []
            for future in as_completed(futures):
                results.append(future.result())

        # Count failures
        failed_count = sum(1 for filename, file_path, error_type, error_msg in results if error_type)

        if failed_count > 0:
            print(f"\n   Total catalog import failures: {failed_count}")

    return ("catalog", len(results) - failed_count, [(fp, et, em) for fn, fp, et, em in results if et])

def _import_plugins(ctx, directory):
    results = []
    failed_count = 0
    if os.path.isdir(directory):
        print("Processing: " + directory)
        files = [(filename, os.path.join(directory, filename))
                 for filename in sorted(os.listdir(directory))
                 if os.path.isfile(os.path.join(directory, filename))]

        def import_plugin_file(file_info):
            filename, file_path = file_info
            try:
                with open(file_path) as f:
                    plugins.create(ctx, file_input=f, force=True)
                return (filename, file_path, None, None)
            except typer.Exit as e:
                return (filename, file_path, "HTTP", "Validation or HTTP error")
            except Exception as e:
                return (filename, file_path, type(e).__name__, str(e))

        # Import all files in parallel
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = {executor.submit(import_plugin_file, file_info): file_info[0] for file_info in files}
            results = []
            for future in as_completed(futures):
                results.append(future.result())

        # Print results in alphabetical order
        failed_count = 0
        for filename, file_path, error_type, error_msg in sorted(results, key=lambda x: x[0]):
            if error_type:
                print(f"   Failed to import {filename}: {error_type} - {error_msg}")
                failed_count += 1
            else:
                print(f"   Importing: {filename}")

    return ("plugins", len(results) - failed_count, [(fp, et, em) for fn, fp, et, em in results if et])

def _import_scorecards(ctx, directory):
    results = []
    failed_count = 0
    if os.path.isdir(directory):
        print("Processing: " + directory)
        files = [(filename, os.path.join(directory, filename))
                 for filename in sorted(os.listdir(directory))
                 if os.path.isfile(os.path.join(directory, filename))]

        def import_scorecard_file(file_info):
            filename, file_path = file_info
            try:
                with open(file_path) as f:
                    scorecards.create(ctx, file_input=f, dry_run=False)
                return (filename, file_path, None, None)
            except typer.Exit as e:
                return (filename, file_path, "HTTP", "Validation or HTTP error")
            except Exception as e:
                return (filename, file_path, type(e).__name__, str(e))

        # Import all files in parallel
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = {executor.submit(import_scorecard_file, file_info): file_info[0] for file_info in files}
            results = []
            for future in as_completed(futures):
                results.append(future.result())

        # Print results in alphabetical order
        failed_count = 0
        for filename, file_path, error_type, error_msg in sorted(results, key=lambda x: x[0]):
            if error_type:
                print(f"   Failed to import {filename}: {error_type} - {error_msg}")
                failed_count += 1
            else:
                print(f"   Importing: {filename}")

    return ("scorecards", len(results) - failed_count, [(fp, et, em) for fn, fp, et, em in results if et])

def _import_workflows(ctx, directory):
    results = []
    failed_count = 0
    if os.path.isdir(directory):
        print("Processing: " + directory)
        files = [(filename, os.path.join(directory, filename))
                 for filename in sorted(os.listdir(directory))
                 if os.path.isfile(os.path.join(directory, filename))]

        def import_workflow_file(file_info):
            filename, file_path = file_info
            try:
                with open(file_path) as f:
                    workflows.create(ctx, file_input=f)
                return (filename, file_path, None, None)
            except typer.Exit as e:
                return (filename, file_path, "HTTP", "Validation or HTTP error")
            except Exception as e:
                return (filename, file_path, type(e).__name__, str(e))

        # Import all files in parallel
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = {executor.submit(import_workflow_file, file_info): file_info[0] for file_info in files}
            results = []
            for future in as_completed(futures):
                results.append(future.result())

        # Print results in alphabetical order
        failed_count = 0
        for filename, file_path, error_type, error_msg in sorted(results, key=lambda x: x[0]):
            if error_type:
                print(f"   Failed to import {filename}: {error_type} - {error_msg}")
                failed_count += 1
            else:
                print(f"   Importing: {filename}")

    return ("workflows", len(results) - failed_count, [(fp, et, em) for fn, fp, et, em in results if et])

@app.command("import")
def import_tenant(
    ctx: typer.Context,
    directory: str = typer.Option(..., "--directory", "-d", help="Location of import directory."),
    force: bool = typer.Option(False, "--force", help="Recreate entities if they already exist."),
):
    """
    Import data into tenant
    """

    client = ctx.obj["client"]

    # Collect statistics from each import
    all_stats = []
    all_stats.append(_import_ip_allowlist(ctx, directory + "/ip-allowlist"))
    all_stats.append(_import_entity_types(ctx, force, directory + "/entity-types"))
    all_stats.append(_import_entity_relationship_types(ctx, directory + "/entity-relationship-types"))
    all_stats.append(_import_catalog(ctx, directory + "/catalog"))
    all_stats.append(_import_entity_relationships(ctx, directory + "/entity-relationships"))
    all_stats.append(_import_plugins(ctx, directory + "/plugins"))
    all_stats.append(_import_scorecards(ctx, directory + "/scorecards"))
    all_stats.append(_import_workflows(ctx, directory + "/workflows"))

    # Print summary
    print("\n" + "="*80)
    print("IMPORT SUMMARY")
    print("="*80)

    total_imported = 0
    total_failed = 0
    all_failures = []

    for import_type, imported, failed in all_stats:
        if imported > 0 or len(failed) > 0:
            total_imported += imported
            total_failed += len(failed)
            print(f"\n{import_type}:")
            print(f"  Imported: {imported}")
            if len(failed) > 0:
                print(f"  Failed:   {len(failed)}")
                all_failures.extend([(import_type, f, e, m) for f, e, m in failed])

    print(f"\nTOTAL: {total_imported} imported, {total_failed} failed")

    if len(all_failures) > 0:
        print("\n" + "="*80)
        print("FAILED IMPORTS")
        print("="*80)
        print("\nThe following files failed to import:\n")

        for import_type, file_path, error_type, error_msg in all_failures:
            print(f"  {file_path}")
            print(f"    Error: {error_type} - {error_msg}")

        print("\n" + "="*80)
        print("RETRY COMMANDS")
        print("="*80)
        print("\nTo retry failed imports, run these commands:\n")

        for import_type, file_path, error_type, error_msg in all_failures:
            if import_type == "catalog":
                print(f"cortex catalog create -f \"{file_path}\"")
            elif import_type == "entity-types":
                print(f"cortex entity-types create --force -f \"{file_path}\"")
            elif import_type == "entity-relationship-types":
                tag = os.path.basename(file_path).replace('.json', '')
                print(f"cortex entity-relationship-types create -f \"{file_path}\"")
            elif import_type == "entity-relationships":
                # These need special handling - would need the relationship type
                print(f"# Manual retry needed for entity-relationships: {file_path}")
            elif import_type == "plugins":
                print(f"cortex plugins create --force -f \"{file_path}\"")
            elif import_type == "scorecards":
                print(f"cortex scorecards create -f \"{file_path}\"")
            elif import_type == "workflows":
                print(f"cortex workflows create -f \"{file_path}\"")
