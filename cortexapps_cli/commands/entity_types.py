from collections import defaultdict
from datetime import datetime
from enum import Enum
import json
from rich import print_json
import typer
from typing_extensions import Annotated

app = typer.Typer(help="Entity Types commands")

@app.command()
def list(
    ctx: typer.Context,
    include_built_in: bool = typer.Option(False, "--include-built-in", "-ib", help="When true, returns the built-in entity types that Cortex provides, such as rds and s3, defaults to false"),
    page: int | None = typer.Option(None, "--page", "-p", help="Page number to return, 0 indexed - omit to fetch all pages"),
    page_size: int | None = typer.Option(None, "--page-size", "-z", help="Page size for results"),
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
    
    client.fetch_or_get("api/v1/catalog/definitions", page, params=params)

@app.command()
def delete(
    ctx: typer.Context,
    entity_type: str = typer.Option(..., "--type", "-ty", help="The entity type"),
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
