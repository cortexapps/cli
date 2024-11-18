import json
from rich import print_json
import typer
from typing_extensions import Annotated

import cortexapps_cli.commands.scorecards_commands.exemptions as exemptions

app = typer.Typer(help="Scorecards commands",
                  no_args_is_help=True)
app.add_typer(exemptions.app, name="exemptions")

@app.command()
def create(
    ctx: typer.Context,
    input: Annotated[typer.FileText, typer.Option(..., "--file", "-f", help="File containing YAML representation of scorecard, can be passed as stdin with -, example: -f-")] = None,
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="When true, this endpoint only validates the descriptor contents and returns any errors or warnings"),
):
    """
    Create or update a Scorecard using the descriptor YAML. The operation is determined by the existence of a Scorecard with the same tag as passed in the descriptor.
    """

    client = ctx.obj["client"]

    params = {
       "dryRun": dry_run
    }       

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}
    
    client.post("api/v1/scorecards/descriptor", params=params, data=input.read(), content_type="application/yaml;charset=UTF-8")

@app.command()
def delete(
    ctx: typer.Context,
    scorecard_tag: str = typer.Option(..., "--scorecard-tag", "-s", help="Unique tag for the scorecard"),
):
    """
    Delete scorecard
    """

    client = ctx.obj["client"]
    
    client.delete("api/v1/scorecards/" + scorecard_tag)

@app.command()
def list(
    ctx: typer.Context,
    show_drafts: bool = typer.Option(False, "--show-drafts", "-s", help="Whether scorecard in draft mode should be included"),
    page: int | None = typer.Option(None, "--page", "-p", help="Page number to return, 0 indexed - omit to fetch all pages"),
    page_size: int | None = typer.Option(None, "--page-size", "-z", help="Page size for results"),
):
    """
    List scorecards
    """

    client = ctx.obj["client"]

    params = {
       "showDrafts": show_drafts
    }       

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}
    
    client.fetch_or_get("api/v1/scorecards", page, params=params)

@app.command()
def shield(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    scorecard_tag: str = typer.Option(..., "--scorecard-tag", "-s", help="Unique tag for the scorecard"),
):
    """
    Retrieve scorecard shields.io badge
    """

    client = ctx.obj["client"]

    r = client.get("api/v1/scorecards/" + scorecard_tag + "/entity/" + tag_or_id + "/badge")
    print_json(data=r)

@app.command()
def get(
    ctx: typer.Context,
    scorecard_tag: str = typer.Option(..., "--scorecard-tag", "-s", help="Unique tag for the scorecard"),
):
    """
    Get scorecard
    """

    client = ctx.obj["client"]
    
    r = client.get("api/v1/scorecards/" + scorecard_tag)
    print_json(data=r)

@app.command()
def descriptor(
    ctx: typer.Context,
    scorecard_tag: str = typer.Option(..., "--scorecard-tag", "-s", help="Unique tag for the scorecard"),
):
    """
    Get scorecards YAML descriptor
    """

    client = ctx.obj["client"]
    
    r = client.get("api/v1/scorecards/" + scorecard_tag + "/descriptor")
    print(r)

@app.command()
def next_steps(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    scorecard_tag: str = typer.Option(..., "--scorecard-tag", "-s", help="Unique tag for the scorecard"),
):
    """
    Retrieve next steps for entity in scorecard
    """

    client = ctx.obj["client"]

    params = {
       "entityTag": tag_or_id
    }       
    
    r = client.get("api/v1/scorecards/" + scorecard_tag + "/next-steps", params=params)
    print_json(data=r)

@app.command()
def scores(
    ctx: typer.Context,
    tag_or_id: str | None = typer.Option(None, "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    scorecard_tag: str = typer.Option(..., "--scorecard-tag", "-s", help="Unique tag for the scorecard"),
    page: int = typer.Option(0, "--page", "-p", help="Page number to return, 0 indexed - omit to fetch all pages"),
    page_size: int | None = typer.Option(None, "--page-size", "-z", help="Page size for results"),
):
    """
    Return latest scores for all entities in the Scorecard
    """

    client = ctx.obj["client"]

    params = {
       "entityTag": tag_or_id,
       "page": page,
       "pageSize": page_size
    }       

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}
    
    client.fetch_or_get("api/v1/scorecards/" + scorecard_tag + "/scores", page, params=params)

