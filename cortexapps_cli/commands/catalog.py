import typer
from typing import Optional, List
from typing_extensions import Annotated

from cortexapps_cli.command_options import ListCommandOptions, CommandOptions
from cortexapps_cli.utils import print_output_with_context, print_output

app = typer.Typer(help="Catalog commands", no_args_is_help=True)

class CatalogCommandOptions:
    include_archived = Annotated[
        Optional[bool],
        typer.Option("--include-archived", "-a", help="Include archived entities", show_default=False)
    ]
    hierarchy_depth = Annotated[
        Optional[str],
        typer.Option("--hierarchy-depth", "-d", help="Depth of the parent / children hierarchy nodes. Can be 'full' or a valid integer", show_default=False)
    ]
    groups = Annotated[
        Optional[str],
        typer.Option("--groups", "-g", help="Filter based on groups, which correspond to the x-cortex-groups field in the Catalog Descriptor. Accepts a comma-delimited list of groups", show_default=False)
    ]
    owners = Annotated[
        Optional[str],
        typer.Option("--owners", "-o", help="Filter based on owner group names, which correspond to the x-cortex-owners field in the Catalog Descriptor. Accepts a comma-delimited list of owner group names", show_default=False)
    ]
    include_hierarchy_fields = Annotated[
        Optional[str],
        typer.Option("--include-hierarchy-fields", "-i", help="List of sub fields to include for hierarchies. Only supports 'groups'", show_default=False)
    ]
    include_nested_fields = Annotated[
        Optional[str],
        typer.Option("--include-nested-fields", "-in", help="List of sub fields to include for different types, for example team:members", show_default=False)
    ]
    include_owners = Annotated[
        Optional[bool],
        typer.Option("--include-owners", "-io", help="Include ownership information for each entity in the response", show_default=False)
    ]
    include_links = Annotated[
        Optional[bool],
        typer.Option("--include-links", "-l", help="Include links for each entity in the response", show_default=False)
    ]
    include_metadata = Annotated[
        Optional[bool],
        typer.Option("--include-metadata", "-m", help="Include custom data for each entity in the response", show_default=False)
    ]
    dry_run = Annotated[
        Optional[bool],
        typer.Option("--dry-run", "-dry", help="When true, only validates the descriptor contents and returns any errors or warnings", show_default=False)
    ]
    append_arrays = Annotated[
        Optional[bool],
        typer.Option("--append-arrays", "-a", help="Default merge behavior is to replace arrays, set this to true to append arrays instead. For simple types, duplicate values will be removed from the merged array", show_default=False)
    ]
    fail_if_not_exist = Annotated[
        Optional[bool],
        typer.Option("--fail-if-not-exist", "-n", help="Default behavior is to upsert the entity, if set command will fail (404) if the entity specified in x-cortex-tag does not exist.", show_default=False)
    ]
    git_repositories = Annotated[
        Optional[str],
        typer.Option("--git-repositories", "-r", help="Supports only GitHub repositories in the org/repo format", show_default=False)
    ]
    types = Annotated[
        Optional[str],
        typer.Option("--types", "-t", help="Filter the response to specific types of entities. By default, this includes services, resources, and domains. Corresponds to the x-cortex-type field in the Entity Descriptor.", show_default=False)
    ]

@app.command(name="list")
def catalog_list(
    ctx: typer.Context,
    include_archived: CatalogCommandOptions.include_archived = False,
    hierarchy_depth: CatalogCommandOptions.hierarchy_depth = 'full',
    groups: CatalogCommandOptions.groups = None,
    owners: CatalogCommandOptions.owners = None,
    include_hierarchy_fields: CatalogCommandOptions.include_hierarchy_fields = None,
    include_nested_fields: CatalogCommandOptions.include_nested_fields = None,
    include_owners: CatalogCommandOptions.include_owners = False,
    include_links: CatalogCommandOptions.include_links = False,
    include_metadata: CatalogCommandOptions.include_metadata = False,
    git_repositories: CatalogCommandOptions.git_repositories = None,
    types: CatalogCommandOptions.types = None,
    page: ListCommandOptions.page = None,
    page_size: ListCommandOptions.page_size = 250,
    table_output: ListCommandOptions.table_output = False,
    csv_output: ListCommandOptions.csv_output = False,
    columns: ListCommandOptions.columns = [],
    no_headers: ListCommandOptions.no_headers = False,
    filters: ListCommandOptions.filters = [],
    sort: ListCommandOptions.sort = [],
    _print: CommandOptions._print = True,
):
    """
    List entities in the catalog
    """
    client = ctx.obj["client"]

    if (table_output or csv_output) and not ctx.params.get('columns'):
        ctx.params['columns'] = [
            "ID=id",
            "Tag=tag",
            "Name=name",
            "Type=type",
            "Git Repository=git.repository",
        ]

    params = {
        "includeArchived": include_archived,
        "hierarchyDepth": hierarchy_depth,
        "groups": groups,
        "owners": owners,
        "includeHierarchyFields": include_hierarchy_fields,
        "includeNestedFields": include_nested_fields,
        "includeOwners": include_owners,
        "includeLinks": include_links,
        "includeMetadata": include_metadata,
        "page": page,
        "pageSize": page_size,
        "gitRepositories": git_repositories,
        "types": types,
    }

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    # for keys that can have multiple values, remove whitespace around comma and split on comma
    for key in ['groups', 'owners', 'gitRepositories', 'types']:
        if key in params:
            params[key] = [x.strip() for x in params[key].split(',')]

    if page is None:
        # if page is not specified, we want to fetch all pages
        r = client.fetch("api/v1/catalog", params=params)
    else:
        # if page is specified, we want to fetch only that page
        r = client.get("api/v1/catalog", params=params)

    if _print:
        data = r
        print_output_with_context(ctx, data)
    else:
        return(r)

@app.command()
def details(
    ctx: typer.Context,
    hierarchy_depth: CatalogCommandOptions.hierarchy_depth = 'full',
    include_hierarchy_fields: CatalogCommandOptions.include_hierarchy_fields = None,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    table_output: ListCommandOptions.table_output = False,
    csv_output: ListCommandOptions.csv_output = False,
    no_headers: ListCommandOptions.no_headers = False,
    columns: ListCommandOptions.columns = [],
    filters: ListCommandOptions.filters = [],
):
    """
    Get details for a specific entity in the catalog
    """
    client = ctx.obj["client"]

    if table_output and csv_output:
        raise typer.BadParameter("Only one of --table and --csv can be specified")

    if (table_output or csv_output) and not ctx.params.get('columns'):
        ctx.params['columns'] = [
            "ID=id",
            "Tag=tag",
            "Name=name",
            "Type=type",
            "Git Repository=git.repository",
        ]

    output_format = "table" if table_output else "csv" if csv_output else "json"

    params = {
        "hierarchyDepth": hierarchy_depth,
        "includeHierarchyFields": include_hierarchy_fields
    }

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    r = client.get("api/v1/catalog/" + tag, params=params)

    data = r if output_format == 'json' else [r]
    print_output_with_context(ctx, data)

@app.command()
def archive(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
):
    """
    Archive an entity
    """
    client = ctx.obj["client"]

    r = client.put("api/v1/catalog/" + tag + "/archive")

@app.command()
def unarchive(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
):
    """
    Unarchive an entity
    """
    client = ctx.obj["client"]

    r = client.put("api/v1/catalog/" + tag + "/unarchive")
    print_output_with_context(ctx, r)

@app.command()
def delete(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
):
    """
    Delete an entity
    """
    client = ctx.obj["client"]

    client.delete("api/v1/catalog/" + tag)

@app.command()
def delete_by_type(
    ctx: typer.Context,
    types: CatalogCommandOptions.types = None,
):
    """
    Dangerous operation that will delete all entities that are of the given type
    """
    client = ctx.obj["client"]

    #TODO: check if types is a regex of form: ([-A-Za-z]+,)+

    params = {
        "types": types
    }

    client.delete("api/v1/catalog", params=params)


@app.command()
def descriptor(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    yaml: bool = typer.Option(False, "--yaml", "-y", help="When true, returns the YAML representation of the descriptor."),
    _print: bool = typer.Option(True, "--print", help="If result should be printed to the terminal", hidden=True),
):
    """
    Retrieve entity descriptor
    """
    client = ctx.obj["client"]

    params = {
        "yaml": str(yaml).lower()
    }

    r = client.get("api/v1/catalog/" + tag + "/openapi", params=params)
    if _print:
        if yaml:
           print(r)
        else:
           print_output_with_context(ctx, r)
           #print(r)
    else:
        if yaml:
           return(r)
        else:
           print_output_with_context(ctx, r)

@app.command()
def create(
    ctx: typer.Context,
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help=" File containing YAML content of entity; can be passed as stdin with -, example: -f-")] = None,
    dry_run: CatalogCommandOptions.dry_run = False,
    _print: CommandOptions._print = True,
):
    """
    Create entity
    """
    client = ctx.obj["client"]

    params = {
        "dryRun": dry_run
    }

    r = client.post("api/v1/open-api", data=file_input.read(), params=params, content_type="application/openapi;charset=UTF-8")
    if _print:
        print_output_with_context(ctx, r)

@app.command()
def patch(
    ctx: typer.Context,
    file_input: Annotated[typer.FileText, typer.Option(..., "--file", "-f", help=" File containing YAML content of entity; can be passed as stdin with -, example: -f-")] = None,
    delete_marker_value = typer.Option("__delete__", "--delete-marker-value", "-dmv", help="Delete keys with this value from the merged yaml, defaults to __delete__, if any values match this, they will not be included in merged YAML. For example my_value: __delete__ will remove my_value from the merged YAML."),
    dry_run: CatalogCommandOptions.dry_run = False,
    append_arrays: CatalogCommandOptions.append_arrays = False,
    fail_if_not_exist: CatalogCommandOptions.fail_if_not_exist = False,
):
    """
    Creates or updates an entity. If the YAML refers to an entity that already exists (as referenced by the x-cortex-tag), this API will merge the specified changes into the existing entity
    """
    client = ctx.obj["client"]

    params = {
        "dryRun":dry_run,
        "appendArrays": append_arrays,
        "deleteMarkerValue": delete_marker_value,
        "failIfEntityDoesNotExist": fail_if_not_exist
    }

    r = client.patch("api/v1/open-api", data=file_input.read(), params=params, content_type="application/openapi;charset=UTF-8")
    print_output_with_context(ctx, r)

@app.command()
def list_descriptors(
    ctx: typer.Context,
    yaml: bool = typer.Option(False, "--yaml", "-y", help="When true, returns the YAML representation of the descriptor."),
    types: CatalogCommandOptions.types = None,
    page: ListCommandOptions.page = None,
    page_size: ListCommandOptions.page_size = 250,
    _print: CommandOptions._print = True,
):
    """
    List entity descriptors
    """
    client = ctx.obj["client"]

    params = {
        "yaml": yaml,
        "types": types,
        "pageSize": page_size,
        "page": page
    }

    r = client.fetch_or_get("api/v1/catalog/descriptors", page, _print, params=params)
    if not _print:
        return(r)

@app.command()
def gitops_log(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
):
    """
    Retrieve most recent GitOps log for entity
    """
    client = ctx.obj["client"]

    r = client.get("api/v1/catalog/" + tag + "/gitops-logs")
    print_output_with_context(ctx, r)

@app.command()
def scorecard_scores(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
):
    """
    Retrieve entity Scorecard scores
    """
    client = ctx.obj["client"]

    r = client.get("api/v1/catalog/" + tag + "/scorecards")
    print_output_with_context(ctx, r)
