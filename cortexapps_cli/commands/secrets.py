import typer
import json
from typing_extensions import Annotated
from cortexapps_cli.utils import print_output_with_context
from cortexapps_cli.command_options import ListCommandOptions

app = typer.Typer(
    help="Secrets commands",
    no_args_is_help=True
)

@app.command()
def list(
    ctx: typer.Context,
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
    List secrets
    """
    client = ctx.obj["client"]

    params = {
       "page": page,
       "pageSize": page_size
    }

    if (table_output or csv_output) and not ctx.params.get('columns'):
        ctx.params['columns'] = [
            "ID=id",
            "Name=name",
            "Tag=tag",
        ]

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    if page is None:
        r = client.fetch("api/v1/secrets", params=params)
    else:
        r = client.get("api/v1/secrets", params=params)
    print_output_with_context(ctx, r)

@app.command()
def get(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="Secret tag or ID"),
):
    """
    Get a secret by tag or ID
    """
    client = ctx.obj["client"]
    r = client.get(f"api/v1/secrets/{tag_or_id}")
    print_output_with_context(ctx, r)

@app.command()
def create(
    ctx: typer.Context,
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File containing secret definition (name, secret, tag); can be passed as stdin with -, example: -f-")] = ...,
):
    """
    Create a secret

    Provide a JSON file with the secret definition including required fields:
    - name: human-readable label for the secret
    - secret: the actual secret value
    - tag: unique identifier for the secret
    """
    client = ctx.obj["client"]
    data = json.loads("".join([line for line in file_input]))
    r = client.post("api/v1/secrets", data=data)
    print_output_with_context(ctx, r)

@app.command()
def update(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="Secret tag or ID"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File containing fields to update (name, secret); can be passed as stdin with -, example: -f-")] = ...,
):
    """
    Update a secret

    Provide a JSON file with the fields to update (name and/or secret are optional).
    """
    client = ctx.obj["client"]
    data = json.loads("".join([line for line in file_input]))
    r = client.put(f"api/v1/secrets/{tag_or_id}", data=data)
    print_output_with_context(ctx, r)

@app.command()
def delete(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="Secret tag or ID"),
):
    """
    Delete a secret
    """
    client = ctx.obj["client"]
    client.delete(f"api/v1/secrets/{tag_or_id}")
