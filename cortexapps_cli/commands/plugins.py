import json
from rich import print_json
import typer
from typing_extensions import Annotated

app = typer.Typer(help="Plugins commands")

@app.command()
def list(
    ctx: typer.Context,
    include_drafts: bool = typer.Option(False, "--include-drafts", "-i", help="Also include plugins that are in draft mode"),
    page: int | None = typer.Option(None, "--page", "-p", help="Page number to return, 0 indexed - omit to fetch all pages"),
    page_size: int | None = typer.Option(None, "--page-size", "-z", help="Page size for results"),
):
    """
    Retrieve a list of all plugins, excluding drafts
    """

    client = ctx.obj["client"]

    params = {
       "page": page,
       "pageSize": page_size
    }       

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}
    
    client.fetch_or_get("api/v1/plugins", page, params=params)

@app.command()
def create(
    ctx: typer.Context,
    plugin_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File containing contents of plugin using schema defined at https://docs.cortex.io/docs/api/create-plugin")] = None
):
    """
    Create a new plugin
    """

    client = ctx.obj["client"]
    
    client.post("api/v1/plugins", data=plugin_input.read())

@app.command()
def delete(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity.")
):
    """
    Delete a plugin by tag
    """

    client = ctx.obj["client"]
    
    client.delete("api/v1/plugins/" + tag_or_id)

@app.command()
def get(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity.")
):
    """
    Retrieve the metadata of a plugin by tag
    """

    client = ctx.obj["client"]
    
    r = client.get("api/v1/plugins/" + tag_or_id)
    print_json(data=r)

@app.command()
def replace(
    ctx: typer.Context,
    plugin_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File containing contents of plugin using schema defined at https://docs.cortex.io/docs/api/create-plugin")] = None,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity.")
):
    """
    Replace an existing plugin by tag
    """

    client = ctx.obj["client"]
    
    client.put("api/v1/plugins/"+ tag_or_id, data=plugin_input.read())
