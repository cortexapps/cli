from collections import defaultdict
from datetime import datetime
from enum import Enum
import json
from rich import print_json
import typer
from typing_extensions import Annotated
from cortexapps_cli.command_options import CommandOptions
from cortexapps_cli.command_options import ListCommandOptions
from cortexapps_cli.utils import print_output_with_context, print_output

app = typer.Typer(help="Entity Types commands", no_args_is_help=True)

@app.command()
def list(
    ctx: typer.Context,
    include_built_in: bool = typer.Option(False, "--include-built-in", "-ib", help="When true, returns the built-in entity types that Cortex provides, such as rds and s3, defaults to false"),
    _print: CommandOptions._print = True,
    page: ListCommandOptions.page = None,
    page_size: ListCommandOptions.page_size = 250,
    table_output: ListCommandOptions.table_output = False,
    csv_output: ListCommandOptions.csv_output = False,
    columns: ListCommandOptions.columns = [],
    filters: ListCommandOptions.filters = [],
    sort: ListCommandOptions.sort = [],
):
    """
    List entity types, excludes Cortex default types of service, domain, and team
    """

    client = ctx.obj["client"]

    params = {
       "includeBuiltIn": include_built_in,
       "page": page,
       "pageSize": page_size,
    }       

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    if (table_output or csv_output) and not ctx.params.get('columns'):
        ctx.params['columns'] = [
            "Type=type",
            "Source=tag",
            "Name=name",
            "Description=description",
        ]

    if page is None:
        # if page is not specified, we want to fetch all pages
        r = client.fetch("api/v1/catalog/definitions", params=params)
    else:
        # if page is specified, we want to fetch only that page
        r = client.get("api/v1/catalog/definitions", params=params)

    if _print:
        data = r
        print_output_with_context(ctx, data)
    else:
        return(r)

@app.command()
def delete(
    ctx: typer.Context,
    entity_type: str = typer.Option(..., "--type", "-t", help="The entity type"),
):
    """
    Delete entity type
    """

    client = ctx.obj["client"]

    client.delete("api/v1/catalog/definitions/" + entity_type)

@app.command()
def create(
    ctx: typer.Context,
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help=" File containing custom entity definition; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Create entity type
    """

    client = ctx.obj["client"]
    data = json.loads("".join([line for line in file_input]))

    r = client.post("api/v1/catalog/definitions/" + entity_type)
    print_json(data=r)

@app.command()
def get(
    ctx: typer.Context,
    entity_type: str = typer.Option(..., "--type", "-t", help="The entity type"),
):
    """
    Retrieve entity type
    """

    client = ctx.obj["client"]

    r = client.get("api/v1/catalog/definitions/" + entity_type)
    print_json(data=r)
