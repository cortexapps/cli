import typer
from typing import Optional, List
from typing_extensions import Annotated

from cortexapps_cli.utils import print_output

app = typer.Typer(help="Catalog commands")

class ListCommandOptions:
    table_output = Annotated[
        Optional[bool],
        typer.Option("--table", help="Output the response as a table", show_default=False)
    ]
    csv_output = Annotated[
        Optional[bool],
        typer.Option("--csv", help="Output the response as CSV", show_default=False)
    ]
    columns = Annotated[
        Optional[List[str]],
        typer.Option("--columns", "-C", help="Columns to include in the table, in the format HeaderName=jsonpath", show_default=False)
    ]
    filter = Annotated[
        Optional[List[str]],
        typer.Option("--filter", "-F", help="Filters to apply on rows, in the format jsonpath=regex", show_default=False)
    ]
    page = Annotated[
        Optional[int],
        typer.Option("--page", "-p", help="Page number to return, 0 indexed - omit to fetch all pages", show_default=False)
    ]
    page_size = Annotated[
        Optional[int],
        typer.Option("--page-size", "-z", help="Page size for results", show_default=False)
    ]


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
    git_repositories = Annotated[
        Optional[str],
        typer.Option("--git-repositories", "-r", help="Supports only GitHub repositories in the org/repo format", show_default=False)
    ]
    types = Annotated[
        Optional[str],
        typer.Option("--types", "-ty", help="Filter the response to specific types of entities. By default, this includes services, resources, and domains. Corresponds to the x-cortex-type field in the Entity Descriptor.", show_default=False)
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
    page: ListCommandOptions.page = None,
    page_size: ListCommandOptions.page_size = 250,
    git_repositories: CatalogCommandOptions.git_repositories = None,
    types: CatalogCommandOptions.types = None,
    table_output: ListCommandOptions.table_output = False,
    csv_output: ListCommandOptions.csv_output = False,
    columns: ListCommandOptions.columns = [],
    filters: ListCommandOptions.filter = [],
):
    client = ctx.obj["client"]

    if table_output and csv_output:
        raise typer.BadParameter("Only one of --table and --csv can be specified")

    if (table_output or csv_output) and not columns:
        columns = [
            "ID=id",
            "Tag=tag",
            "Name=name",
            "Type=type",
            "Git Repository=git.repository",
        ]

    output_format = "table" if table_output else "csv" if csv_output else "json"

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

    data = r if output_format == 'json' else r.get('entities', [])
    print_output(data=data, columns=columns, filters=filters, output_format=output_format)

@app.command()
def details(
    ctx: typer.Context,
    hierarchy_depth: CatalogCommandOptions.hierarchy_depth = 'full',
    include_hierarchy_fields: CatalogCommandOptions.include_hierarchy_fields = None,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    table_output: ListCommandOptions.table_output = False,
    csv_output: ListCommandOptions.csv_output = False,
    columns: ListCommandOptions.columns = [],
    filters: ListCommandOptions.filter = [],
):
    client = ctx.obj["client"]

    if table_output and csv_output:
        raise typer.BadParameter("Only one of --table and --csv can be specified")

    if (table_output or csv_output) and not columns:
        columns = [
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
    print_output(data=data, columns=columns, filters=filters, output_format=output_format)
