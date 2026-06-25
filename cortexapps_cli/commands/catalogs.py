import json
from rich import print_json
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
    _print: CommandOptions._print = True,
    table_output: ListCommandOptions.table_output = False,
    csv_output: ListCommandOptions.csv_output = False,
    columns: ListCommandOptions.columns = [],
    no_headers: ListCommandOptions.no_headers = False,
    filters: ListCommandOptions.filters = [],
    sort: ListCommandOptions.sort = [],
):
    """
    List all catalogs.
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

    result = client.get("api/v1/catalogs")

    if _print:
        print_output_with_context(ctx, result)
    else:
        return result

@app.command()
def get(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The slug or unique ID of the catalog"),
):
    """
    Retrieve a catalog by its slug or ID.
    """
    client = ctx.obj["client"]

    result = client.get("api/v1/catalogs/" + tag_or_id)
    print_json(data=result)

@app.command()
def create(
    ctx: typer.Context,
    file_input: Annotated[typer.FileText, typer.Option(..., "--file", "-f", help="File containing JSON body of the catalog request, can be passed as stdin with -, example: -f-")] = None,
):
    """
    Create a catalog. The JSON body should include: name, slug, iconTag, and optionally description, isDraft, filter, relationshipTypeId, catalogType.
    """
    client = ctx.obj["client"]
    data = json.loads("".join([line for line in file_input]))

    result = client.post("api/v1/catalogs", data=data)
    print_json(data=result)

@app.command()
def delete(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The slug or unique ID of the catalog"),
):
    """
    Delete a catalog by its slug or ID.
    """
    client = ctx.obj["client"]

    client.delete("api/v1/catalogs/" + tag_or_id)
