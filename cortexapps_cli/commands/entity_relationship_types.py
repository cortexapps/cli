import typer
import json
from typing_extensions import Annotated
from cortexapps_cli.utils import print_output_with_context
from cortexapps_cli.command_options import CommandOptions, ListCommandOptions

app = typer.Typer(
    help="Entity Relationship Types commands",
    no_args_is_help=True
)

@app.command()
def list(
    ctx: typer.Context,
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
    List entity relationship types
    """
    client = ctx.obj["client"]

    params = {
       "page": page,
       "pageSize": page_size
    }

    if (table_output or csv_output) and not ctx.params.get('columns'):
        ctx.params['columns'] = [
            "Tag=tag",
            "Name=name",
            "Description=description",
        ]

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    if page is None:
        r = client.fetch("api/v1/relationship-types", params=params)
    else:
        r = client.get("api/v1/relationship-types", params=params)

    if _print:
        print_output_with_context(ctx, r)
    else:
        return r

@app.command()
def get(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="Relationship type tag"),
):
    """
    Get a relationship type by tag
    """
    client = ctx.obj["client"]
    r = client.get(f"api/v1/relationship-types/{tag}")
    print_output_with_context(ctx, r)

@app.command()
def create(
    ctx: typer.Context,
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File containing relationship type definition; can be passed as stdin with -, example: -f-")] = ...,
    _print: CommandOptions._print = True,
):
    """
    Create a relationship type

    Provide a JSON file with the relationship type definition including required fields:
    - tag: unique identifier
    - name: human-readable name
    - definitionLocation: SOURCE, DESTINATION, or BOTH
    - allowCycles: boolean
    - createCatalog: boolean
    - isSingleSource: boolean
    - isSingleDestination: boolean
    - sourcesFilter: object with include/types configuration
    - destinationsFilter: object with include/types configuration
    - inheritances: array of inheritance settings
    """
    client = ctx.obj["client"]
    data = json.loads("".join([line for line in file_input]))
    r = client.post("api/v1/relationship-types", data=data)
    if _print:
        print_output_with_context(ctx, r)

@app.command()
def update(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="Relationship type tag"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File containing relationship type definition; can be passed as stdin with -, example: -f-")] = ...,
    _print: CommandOptions._print = True,
):
    """
    Update a relationship type

    Provide a JSON file with the relationship type definition to update.
    """
    client = ctx.obj["client"]
    data = json.loads("".join([line for line in file_input]))
    r = client.put(f"api/v1/relationship-types/{tag}", data=data)
    if _print:
        print_output_with_context(ctx, r)

@app.command()
def delete(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="Relationship type tag"),
):
    """
    Delete a relationship type
    """
    client = ctx.obj["client"]
    client.delete(f"api/v1/relationship-types/{tag}")
