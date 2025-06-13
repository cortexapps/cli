import typer
import json
from rich import print_json

app = typer.Typer(help="On Call commands", no_args_is_help=True)

@app.command()
def get(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity.")
):
    """
    Retrieve current on-call for entity
    """

    client = ctx.obj["client"]

    r = client.get("api/v1/catalog/" + tag_or_id + "/integrations/oncall/current")
    print_json(data=r)

@app.command()
def get_registration(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity.")
):
    """
    Retrieve on-call registration for entity
    """

    client = ctx.obj["client"]

    r = client.get("api/v1/catalog/" + tag_or_id + "/integrations/oncall/registration")
    print_json(data=r)
