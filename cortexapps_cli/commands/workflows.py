import typer
from cortexapps_cli.utils import print_output_with_context
from typing_extensions import Annotated
import json

app = typer.Typer(help="Workflows commands", no_args_is_help=True)

@app.command()
def list(
    ctx: typer.Context,
    include_actions: bool = typer.Option(False, "--include-actions", "-i", help="When true, returns the list of actions for each workflow. Defaults to false"),
    search_query: str = typer.Option(None, "--search-query", "-s", help="When set, only returns workflows with the given substring in the name or description"),
    page: int | None = typer.Option(None, "--page", "-p", help="Page number to return, 0 indexed - omit to fetch all pages"),
    page_size: int | None = typer.Option(None, "--page-size", "-z", help="Page size for results"),
):
    """
    Get users based on provided criteria.  API key must have the View workflows permission
    """

    client = ctx.obj["client"]

    params = {
       "includeActions": include_actions,
       "searchQuery": search_query,
       "page": page,
       "pageSize": page_size
    }       

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}
    
    r = client.get("api/v1/workflows", params=params)
    print_output_with_context(ctx, r)

@app.command()
def get(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag or unique, auto-generated identifier for the workflow"),
):
    """
    Retrieve workflow by tag or ID.  API key must have the View workflows permission.
    """

    client = ctx.obj["client"]

    r = client.get("api/v1/workflows/" + tag)
    print_output_with_context(ctx, r)

@app.command()
def delete(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag or unique, auto-generated identifier for the workflow"),
):
    """
    Delete workflow by tag or ID.  API key must have the Edit workflows permission.
    """

    client = ctx.obj["client"]

    r = client.delete("api/v1/workflows/" + tag)

@app.command()
def create(
    ctx: typer.Context,
    file_input: Annotated[typer.FileText, typer.Option(..., "--file", "-f", help=" File containing workflow definition; can be passed as stdin with -, example: -f-")],
):
    """
    Create or update new workflow.  API key must have the Edit workflows permission.  Note: If a workflow with the same tag already exists, it will be updated.
    """

    client = ctx.obj["client"]
    data = json.loads("".join([line for line in file_input]))

    r = client.post("api/v1/workflows", data=data)
    print_output_with_context(ctx, r)
