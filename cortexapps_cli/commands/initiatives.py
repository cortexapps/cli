import json
from rich import print_json
import typer
from typing_extensions import Annotated
from cortexapps_cli.command_options import CommandOptions
from cortexapps_cli.command_options import ListCommandOptions
from cortexapps_cli.utils import print_output_with_context, print_output

app = typer.Typer(
    help="Initiatives commands",
    no_args_is_help=True
)

@app.command()
def create(
    ctx: typer.Context,
    file_input: Annotated[typer.FileText, typer.Option(..., "--file", "-f", help="File containing JSON body of request, can be passed as stdin with -, example: -f-")] = None,
):
    """
    Create an Initiative.  API key must have the Edit Initiative permission.
    """
    
description
levels
rules
exclude-groups
include-groups
query
types-include
types-exclude
isdraft
name
notification-disabled
notification-replyto
notification-time-interval
notification-time-unit
scorecard-tag
target-date
{
  "description": "text",
  "emphasizedLevels": [
    {
      "rank": 1
    }
  ],
  "emphasizedRules": [
    {
      "expression": "text"
    }
  ],
  "filter": {
    "groups": {
      "exclude": [
        "text"
      ],
      "include": [
        "text"
      ]
    },
    "query": "text",
    "types": {
      "exclude": [
        "text"
      ],
      "include": [
        "text"
      ]
    }
  },
  "isDraft": true,
  "name": "text",
  "notificationSchedule": {
    "isDisabled": true,
    "replyToEmails": [
      "text"
    ],
    "timeInterval": 1,
    "timeUnit": "text"
  },
  "scorecardTag": "text",
  "targetDate": "2025-06-10"
}

    client = ctx.obj["client"]

    params = {
       "dryRun": dry_run
    }       

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}
    
    client.post("api/v1/initiatives", params=params, data=input.read())

@app.command()
def delete(
    ctx: typer.Context,
    cid: str = typer.Option(..., "--cid", "-c", help="Unique Cortex ID for the initiative"),
):
    """
    Delete initiative.  API key must have the Edit Initiatives permission.
    """

    client = ctx.obj["client"]
    
    r = client.delete("api/v1/initiatives/" + cid)

@app.command()
def list(
    ctx: typer.Context,
    include_drafts: bool = typer.Option(False, "--include-drafts", "-d", help="Whether scorecard in draft mode should be included"),
    include_expired: bool = typer.Option(False, "--include-expired", "-e", help="Whether scorecard in draft mode should be included"),
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
    List initiatives
    """

    client = ctx.obj["client"]

    params = {
       "page": page,
       "pageSize": page_size,
       "includeDrafts": include_drafts,
       "includeExpired": include_expired
    }       

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    if (table_output or csv_output) and not ctx.params.get('columns'):
        ctx.params['columns'] = [
            "CId=cid",
            "Name=name",
            "Description=description",
            "TargetDate=targetDate",
            "ScorecardTag=scorecardTag",
            "ScorecardName=scorecardName",
            "IsDraft=isDraft",
        ]

    if page is None:
        r = client.fetch("api/v1/initiatives", params=params)
    else:
        r = client.get("api/v1/initiatives", params=params)

    if _print:
        data = r
        print_output_with_context(ctx, data)
    else:
        return(r)

@app.command()
def get(
    ctx: typer.Context,
    cid: str = typer.Option(..., "--cid", "-c", help="Unique Cortex ID for the initiative"),
):
    """
    Get initiative.  API key must have the View Initiatives permission.
    """

    client = ctx.obj["client"]
    
    r = client.get("api/v1/initiatives/" + cid)
    print_json(data=r)
