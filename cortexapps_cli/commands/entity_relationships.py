import typer
import json
from typing_extensions import Annotated
from cortexapps_cli.utils import print_output_with_context
from cortexapps_cli.command_options import CommandOptions, ListCommandOptions

app = typer.Typer(
    help="Entity Relationships commands (Beta)",
    no_args_is_help=True
)

@app.command()
def list(
    ctx: typer.Context,
    relationship_type: str = typer.Option(..., "--relationship-type", "-r", help="Relationship type tag"),
    _print: CommandOptions._print = True,
    page: ListCommandOptions.page = None,
    page_size: ListCommandOptions.page_size = 250,
    table_output: ListCommandOptions.table_output = False,
    csv_output: ListCommandOptions.csv_output = False,
    columns: ListCommandOptions.columns = [],
    no_headers: ListCommandOptions.no_headers = False,
    filters: ListCommandOptions.filters = [],
    sort: ListCommandOptions.sort = [],
):
    """
    List all relationships for a given relationship type
    """
    client = ctx.obj["client"]

    params = {
       "page": page,
       "pageSize": page_size
    }

    if (table_output or csv_output) and not ctx.params.get('columns'):
        ctx.params['columns'] = [
            "Source=source.tag",
            "Destination=destination.tag",
            "Provider=providerType",
        ]

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    if page is None:
        r = client.fetch(f"api/v1/relationships/{relationship_type}", params=params)
    else:
        r = client.get(f"api/v1/relationships/{relationship_type}", params=params)

    if _print:
        print_output_with_context(ctx, r)
    else:
        return r

@app.command()
def list_destinations(
    ctx: typer.Context,
    entity_tag: str = typer.Option(..., "--entity-tag", "-e", help="Entity tag or ID"),
    relationship_type: str = typer.Option(..., "--relationship-type", "-r", help="Relationship type tag"),
    depth: int = typer.Option(1, "--depth", "-d", help="Maximum hierarchy depth"),
    include_archived: bool = typer.Option(False, "--include-archived", help="Include archived entities"),
):
    """
    List destination entities for a given source entity and relationship type
    """
    client = ctx.obj["client"]

    params = {
        "depth": depth,
        "includeArchived": include_archived
    }

    r = client.get(f"api/v1/catalog/{entity_tag}/relationships/{relationship_type}/destinations", params=params)
    print_output_with_context(ctx, r)

@app.command()
def list_sources(
    ctx: typer.Context,
    entity_tag: str = typer.Option(..., "--entity-tag", "-e", help="Entity tag or ID"),
    relationship_type: str = typer.Option(..., "--relationship-type", "-r", help="Relationship type tag"),
    depth: int = typer.Option(1, "--depth", "-d", help="Maximum hierarchy depth"),
    include_archived: bool = typer.Option(False, "--include-archived", help="Include archived entities"),
):
    """
    List source entities for a given destination entity and relationship type
    """
    client = ctx.obj["client"]

    params = {
        "depth": depth,
        "includeArchived": include_archived
    }

    r = client.get(f"api/v1/catalog/{entity_tag}/relationships/{relationship_type}/sources", params=params)
    print_output_with_context(ctx, r)

@app.command()
def add_destinations(
    ctx: typer.Context,
    entity_tag: str = typer.Option(..., "--entity-tag", "-e", help="Entity tag or ID"),
    relationship_type: str = typer.Option(..., "--relationship-type", "-r", help="Relationship type tag"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File containing destinations array; can be passed as stdin with -, example: -f-")] = ...,
    force: bool = typer.Option(False, "--force", help="Override catalog descriptor values"),
):
    """
    Add destination entities for a given source entity

    Provide a JSON file with: {"destinations": ["entity-1", "entity-2"]}
    """
    client = ctx.obj["client"]
    data = json.loads("".join([line for line in file_input]))

    params = {"force": force} if force else {}

    r = client.post(f"api/v1/catalog/{entity_tag}/relationships/{relationship_type}/destinations", data=data, params=params)
    print_output_with_context(ctx, r)

@app.command()
def add_sources(
    ctx: typer.Context,
    entity_tag: str = typer.Option(..., "--entity-tag", "-e", help="Entity tag or ID"),
    relationship_type: str = typer.Option(..., "--relationship-type", "-r", help="Relationship type tag"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File containing sources array; can be passed as stdin with -, example: -f-")] = ...,
    force: bool = typer.Option(False, "--force", help="Override catalog descriptor values"),
):
    """
    Add source entities for a given destination entity

    Provide a JSON file with: {"sources": ["entity-1", "entity-2"]}
    """
    client = ctx.obj["client"]
    data = json.loads("".join([line for line in file_input]))

    params = {"force": force} if force else {}

    r = client.post(f"api/v1/catalog/{entity_tag}/relationships/{relationship_type}/sources", data=data, params=params)
    print_output_with_context(ctx, r)

@app.command()
def update_destinations(
    ctx: typer.Context,
    entity_tag: str = typer.Option(..., "--entity-tag", "-e", help="Entity tag or ID"),
    relationship_type: str = typer.Option(..., "--relationship-type", "-r", help="Relationship type tag"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File containing destinations array; can be passed as stdin with -, example: -f-")] = ...,
    force: bool = typer.Option(False, "--force", help="Override catalog descriptor values"),
):
    """
    Replace all destination entities for a given source entity

    Provide a JSON file with: {"destinations": ["entity-1", "entity-2"]}
    """
    client = ctx.obj["client"]
    data = json.loads("".join([line for line in file_input]))

    params = {"force": force} if force else {}

    r = client.put(f"api/v1/catalog/{entity_tag}/relationships/{relationship_type}/destinations", data=data, params=params)
    print_output_with_context(ctx, r)

@app.command()
def update_sources(
    ctx: typer.Context,
    entity_tag: str = typer.Option(..., "--entity-tag", "-e", help="Entity tag or ID"),
    relationship_type: str = typer.Option(..., "--relationship-type", "-r", help="Relationship type tag"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File containing sources array; can be passed as stdin with -, example: -f-")] = ...,
    force: bool = typer.Option(False, "--force", help="Override catalog descriptor values"),
):
    """
    Replace all source entities for a given destination entity

    Provide a JSON file with: {"sources": ["entity-1", "entity-2"]}
    """
    client = ctx.obj["client"]
    data = json.loads("".join([line for line in file_input]))

    params = {"force": force} if force else {}

    r = client.put(f"api/v1/catalog/{entity_tag}/relationships/{relationship_type}/sources", data=data, params=params)
    print_output_with_context(ctx, r)

@app.command()
def add_bulk(
    ctx: typer.Context,
    relationship_type: str = typer.Option(..., "--relationship-type", "-r", help="Relationship type tag"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File containing relationships array; can be passed as stdin with -, example: -f-")] = ...,
    force: bool = typer.Option(False, "--force", help="Override catalog descriptor values"),
):
    """
    Add multiple relationships in bulk

    Provide a JSON file with: {"relationships": [{"source": "tag1", "destination": "tag2"}]}
    """
    client = ctx.obj["client"]
    data = json.loads("".join([line for line in file_input]))

    params = {"force": force} if force else {}

    r = client.post(f"api/v1/relationships/{relationship_type}", data=data, params=params)
    print_output_with_context(ctx, r)

@app.command()
def update_bulk(
    ctx: typer.Context,
    relationship_type: str = typer.Option(..., "--relationship-type", "-r", help="Relationship type tag"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File containing relationships array; can be passed as stdin with -, example: -f-")] = ...,
    force: bool = typer.Option(False, "--force", help="Override catalog descriptor values"),
    _print: CommandOptions._print = True,
):
    """
    Replace all relationships for a given relationship type

    Provide a JSON file with: {"relationships": [{"source": "tag1", "destination": "tag2"}]}
    """
    client = ctx.obj["client"]
    data = json.loads("".join([line for line in file_input]))

    params = {"force": force} if force else {}

    r = client.put(f"api/v1/relationships/{relationship_type}", data=data, params=params)
    if _print:
        print_output_with_context(ctx, r)
