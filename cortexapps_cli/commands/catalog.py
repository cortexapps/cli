import typer

from rich import print_json

app = typer.Typer(help="Catalog commands")

@app.command()
def list(
    ctx: typer.Context,
    include_archived: bool = typer.Option(False, "--include-archived", "-a", help="Include archived entities"),
    hierarchy_depth: str = typer.Option('full', "--hierarchy-depth", "-d", help="Depth of the parent / children hierarchy nodes. Can be 'full' or a valid integer"),
    groups: str = typer.Option(None, "--groups", "-g", help="Filter based on groups, which correspond to the x-cortex-groups field in the Catalog Descriptor. Accepts a comma-delimited list of groups"),
    owners: str = typer.Option(None, "--owners", "-o", help="Filter based on owner group names, which correspond to the x-cortex-owners field in the Catalog Descriptor. Accepts a comma-delimited list of owner group names"),
    include_hierarchy_fields: str = typer.Option(None, "--include-hierarchy-fields", "-i", help="List of sub fields to include for hierarchies. Only supports 'groups'"),
    include_nested_fields: str = typer.Option(None, "--include-nested-fields", "-in", help="List of sub fields to include for different types, for example team:members"),
    include_owners: bool = typer.Option(False, "--include-owners", "-io", help="Include ownership information for each entity in the response"),
    include_links: bool = typer.Option(False, "--include-links", "-l", help="Include links for each entity in the response"),
    include_metadata: bool = typer.Option(False, "--include-metadata", "-m", help="Include custom data for each entity in the response"),
    page: int | None = typer.Option(None, "--page", "-p", help="Page number to return, 0 indexed - omit to fetch all pages"),
    page_size: int | None = typer.Option(None, "--page-size", "-z", help="Page size for results"),
    git_repositories: str = typer.Option(None, "--git-repositories", "-r", help="Supports only GitHub repositories in the org/repo format"),
    types: str = typer.Option(None, "--types", "-t", help="Filter the response to specific types of entities. By default, this includes services, resources, and domains. Corresponds to the x-cortex-type field in the Entity Descriptor."),
):
    client = ctx.obj["client"]

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
        pass
    else:
        # if page is specified, we want to fetch only that page
        r = client.get("api/v1/catalog", params=params)
        pass

    print_json(data=r)
