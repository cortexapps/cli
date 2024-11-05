import json
from rich import print_json
import typer

app = typer.Typer(help="Groups commands")

@app.command()
def get(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    page: int | None = typer.Option(None, "--page", "-p", help="Page number to return, 0 indexed - omit to fetch all pages"),
    page_size: int | None = typer.Option(None, "--page-size", "-z", help="Page size for results"),
):
    """
    Get groups for entity.
    """

    client = ctx.obj["client"]

    params = {
       "page": page,
       "pageSize": page_size
    }       

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}
    
    client.fetch_or_get("api/v1/catalog/" + tag_or_id + "/groups", page, params=params)

@app.command()
def add(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    groups: str = typer.Option(..., "--groups", "-g", help="Comma-delimited list of groups to add to the entity")
):
    """
    Add groups to entity.
    """

    client = ctx.obj["client"]

    data = {
       "groups": [{"tag": x.strip()} for x in groups.split(',')]
    }
    
    r = client.put("api/v1/catalog/" + tag_or_id + "/groups", data=data)
    print_json(data=r)

@app.command()
def delete(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    groups: str = typer.Option(..., "--groups", "-g", help="Comma-delimited list of groups to delete from the entity")
):
    """
    Delete groups from entity.
    """

    client = ctx.obj["client"]

    data = {
       "groups": [{"tag": x.strip()} for x in groups.split(',')]
    }
    
    r = client.delete("api/v1/catalog/" + tag_or_id + "/groups", data=data)
