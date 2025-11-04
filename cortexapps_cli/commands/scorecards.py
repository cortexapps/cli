import json
from rich import print_json
import typer
from typing_extensions import Annotated
from cortexapps_cli.command_options import CommandOptions
from cortexapps_cli.command_options import ListCommandOptions
from cortexapps_cli.utils import print_output_with_context, print_output

import cortexapps_cli.commands.scorecards_commands.exemptions as exemptions

app = typer.Typer(
    help="Scorecards commands",
    no_args_is_help=True
)
app.add_typer(exemptions.app, name="exemptions")

@app.command()
def create(
    ctx: typer.Context,
    file_input: Annotated[typer.FileText, typer.Option(..., "--file", "-f", help="File containing YAML representation of scorecard, can be passed as stdin with -, example: -f-")] = None,
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
    
    client.post("api/v1/scorecards/descriptor", params=params, data=file_input.read(), content_type="application/yaml;charset=UTF-8")

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
    List scorecards
    """

    client = ctx.obj["client"]

    params = {
       "page": page,
       "pageSize": page_size,
       "showDrafts": show_drafts
    }       

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    if (table_output or csv_output) and not ctx.params.get('columns'):
        ctx.params['columns'] = [
            "Name=name",
            "Tag=tag",
            "Description=description",
            "IsDraft=isDraft",
        ]

    if page is None:
        # if page is not specified, we want to fetch all pages
        r = client.fetch("api/v1/scorecards", params=params)
    else:
        # if page is specified, we want to fetch only that page
        r = client.get("api/v1/scorecards", params=params)

    if _print:
        data = r
        print_output_with_context(ctx, data)
    else:
        return(r)

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
    _print: bool = typer.Option(True, "--print", help="If result should be printed to the terminal", hidden=True),
):
    """
    Get scorecards YAML descriptor
    """

    client = ctx.obj["client"]
    
    r = client.get("api/v1/scorecards/" + scorecard_tag + "/descriptor")
    if _print:
        print(r)
    else:
        return(r)

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
    _print: bool = typer.Option(True, "--print", help="If result should be printed to the terminal", hidden=True),
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

    client.fetch_or_get("api/v1/scorecards/" + scorecard_tag + "/scores", page, _print, params=params)

@app.command(name="trigger-evaluation")
def trigger_evaluation(
    ctx: typer.Context,
    scorecard_tag: str = typer.Option(..., "--scorecard-tag", "-s", help="Unique tag for the scorecard"),
    entity_tag: str = typer.Option(..., "--entity-tag", "-e", help="The entity's unique tag (x-cortex-tag)"),
):
    """
    Trigger score evaluation for a specific entity in a scorecard
    """

    client = ctx.obj["client"]

    client.post(f"api/v1/scorecards/{scorecard_tag}/entity/{entity_tag}/scores")
    print(f"Scorecard evaluation triggered successfully for entity '{entity_tag}' in scorecard '{scorecard_tag}'")

