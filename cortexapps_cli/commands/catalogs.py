from cortexapps_cli.command_options import CommandOptions
from cortexapps_cli.command_options import ListCommandOptions
from cortexapps_cli.utils import print_output_with_context, print_output
from typing_extensions import Annotated
import json
import typer
import yaml

app = typer.Typer(
    help="Catalog page commands",
    no_args_is_help=True
)

def _read_definition(file_input):
    """Parse a catalog page definition from a JSON or YAML file into a dict.

    The definition is always sent to the API as JSON, so a YAML file is parsed
    and re-serialized rather than posted verbatim.
    """
    content = file_input.read()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    try:
        return yaml.safe_load(content)
    except yaml.YAMLError:
        raise typer.BadParameter("Input file is neither valid JSON nor YAML.")

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
    List catalog pages.
    """

    client = ctx.obj["client"]

    params = {
       "page": page,
       "pageSize": page_size
    }

    if (table_output or csv_output) and not ctx.params.get('columns'):
        ctx.params['columns'] = [
            "Name=name",
            "Slug=slug",
            "Type=type",
            "Description=description",
        ]

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    if page is None:
        # if page is not specified, we want to fetch all pages
        r = client.fetch("api/v1/catalog-pages", params=params)
    else:
        # if page is specified, we want to fetch only that page
        r = client.get("api/v1/catalog-pages", params=params)

    if _print:
        print_output_with_context(ctx, r)
    else:
        return(r)

@app.command()
def get(
    ctx: typer.Context,
    slug: str = typer.Option(..., "--slug", "-s", help="The slug of the catalog page"),
    _print: CommandOptions._print = True,
):
    """
    Retrieve a catalog page by slug.
    """

    client = ctx.obj["client"]

    r = client.get("api/v1/catalog-pages/" + slug)

    if _print:
        print_output_with_context(ctx, r)
    else:
        return(r)

@app.command()
def create(
    ctx: typer.Context,
    file_input: Annotated[typer.FileText, typer.Option(..., "--file", "-f", help="File containing the catalog page definition (JSON or YAML); can be passed as stdin with -, example: -f-")],
):
    """
    Create a catalog page, or replace the existing one with the same slug.  API key must have the Edit Catalogs permission.
    """

    client = ctx.obj["client"]

    data = _read_definition(file_input)
    r = client.post("api/v1/catalog-pages", data=data)
    print_output(r)

@app.command()
def delete(
    ctx: typer.Context,
    slug: str = typer.Option(..., "--slug", "-s", help="The slug of the catalog page"),
):
    """
    Delete a catalog page by slug.  API key must have the Edit Catalogs permission.
    """

    client = ctx.obj["client"]

    client.delete("api/v1/catalog-pages/" + slug)
