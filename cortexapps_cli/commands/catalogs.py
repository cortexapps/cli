import json
from typing import Optional
import typer
from typing_extensions import Annotated
from cortexapps_cli.command_options import CommandOptions
from cortexapps_cli.command_options import ListCommandOptions
from cortexapps_cli.utils import print_output_with_context

app = typer.Typer(
    help="Catalogs commands — manage catalog pages (distinct from 'catalog' which manages entities)",
    no_args_is_help=True
)

@app.command(name="list")
def catalogs_list(
    ctx: typer.Context,
    page: ListCommandOptions.page = None,
    page_size: ListCommandOptions.page_size = 250,
    _print: CommandOptions._print = True,
    table_output: ListCommandOptions.table_output = False,
    csv_output: ListCommandOptions.csv_output = False,
    columns: ListCommandOptions.columns = [],
    no_headers: ListCommandOptions.no_headers = False,
    filters: ListCommandOptions.filters = [],
    sort: ListCommandOptions.sort = [],
):
    """
    List all catalogs. API key must have the View catalogs permission.
    """
    client = ctx.obj["client"]

    if (table_output or csv_output) and not ctx.params.get('columns'):
        ctx.params['columns'] = [
            "Name=name",
            "Slug=slug",
            "Description=description",
            "Icon=iconTag",
            "IsDraft=isDraft",
            "Type=catalogType",
        ]

    params = {k: v for k, v in {"page": page, "pageSize": page_size}.items() if v is not None}

    result = client.fetch("api/v1/catalogs", params=params) if page is None else client.get("api/v1/catalogs", params=params)

    if _print:
        print_output_with_context(ctx, result)
    else:
        return result


@app.command()
def get(
    ctx: typer.Context,
    slug: str = typer.Option(..., "--slug", "-s", help="The slug of the catalog"),
    _print: CommandOptions._print = True,
):
    """
    Retrieve a catalog by its slug. API key must have the View catalogs permission.
    """
    client = ctx.obj["client"]

    result = client.get("api/v1/catalogs/" + slug)

    if _print:
        print_output_with_context(ctx, result)
    else:
        return result


@app.command()
def create(
    ctx: typer.Context,
    file_input: Annotated[
        typer.FileText,
        typer.Option(..., "--file", "-f", help="File containing JSON catalog definition; use - for stdin, e.g. -f-"),
    ],
    mode: Optional[str] = typer.Option(
        None,
        "--mode",
        "-m",
        help="UPSERT (default): create or replace existing catalog. CREATE: fail if slug already exists.",
    ),
    _print: CommandOptions._print = True,
):
    """
    Create or replace a catalog. API key must have the Edit catalogs permission.

    JSON fields: name (required), slug (required), iconTag (required), description,
    isDraft, filter, relationshipTypeTag, catalogType (FILTER|RELATIONSHIP_TYPE|DOMAIN).
    """
    client = ctx.obj["client"]
    data = json.loads(file_input.read())

    params = {}
    if mode:
        params["mode"] = mode.upper()

    result = client.post("api/v1/catalogs", data=data, params=params if params else None)

    if _print:
        print_output_with_context(ctx, result)
    else:
        return result


@app.command()
def delete(
    ctx: typer.Context,
    slug: str = typer.Option(..., "--slug", "-s", help="The slug of the catalog to delete"),
):
    """
    Delete a catalog by its slug. API key must have the Edit catalogs permission.
    """
    client = ctx.obj["client"]

    client.delete("api/v1/catalogs/" + slug)
