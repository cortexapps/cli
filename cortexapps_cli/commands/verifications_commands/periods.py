import typer
from typing import Optional
from typing_extensions import Annotated

from cortexapps_cli.command_options import ListCommandOptions
from cortexapps_cli.utils import print_output_with_context

app = typer.Typer(help="Verification periods commands", no_args_is_help=True)


class PeriodsCommandOptions:
    period_cid = Annotated[
        str,
        typer.Option("--period-cid", "-p", help="The CID of the verification period"),
    ]
    is_active = Annotated[
        Optional[bool],
        typer.Option("--is-active", "-a", help="Filter to only active or inactive periods", show_default=False),
    ]


@app.command(name="list")
def periods_list(
    ctx: typer.Context,
    is_active: PeriodsCommandOptions.is_active = None,
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
    List verification periods
    """
    client = ctx.obj["client"]

    if (table_output or csv_output) and not ctx.params.get("columns"):
        ctx.params["columns"] = [
            "CID=cid",
            "Name=name",
            "Start=startDate",
            "End=endDate",
            "Pending=counts.pending",
            "Correct=counts.verifiedCorrect",
            "Incorrect=counts.verifiedIncorrect",
        ]

    params = {
        "isActive": is_active,
        "page": page,
        "pageSize": page_size,
    }
    params = {k: v for k, v in params.items() if v is not None}

    if page is None:
        r = client.fetch("api/v1/verification-periods", params=params)
    else:
        r = client.get("api/v1/verification-periods", params=params)

    print_output_with_context(ctx, r)


@app.command()
def get(
    ctx: typer.Context,
    period_cid: PeriodsCommandOptions.period_cid = ...,
):
    """
    Get a verification period by CID
    """
    client = ctx.obj["client"]
    r = client.get(f"api/v1/verification-periods/{period_cid}")
    print_output_with_context(ctx, r)


@app.command()
def create(
    ctx: typer.Context,
    file_input: Annotated[
        typer.FileText,
        typer.Option("--file", "-f", help="File containing JSON body of the verification period; can be passed as stdin with -, example: -f-"),
    ] = None,
):
    """
    Create a verification period

    Example file input (period.json):

    \b
    {
      "name": "Q4 2026 Verification",
      "startDate": "2026-10-01T00:00:00",
      "endDate": "2026-12-31T00:00:00",
      "scope": {
        "entityGroups": [],
        "excludedEntityGroups": [],
        "types": ["service"]
      },
      "requiredRoles": [],
      "requiredCustomRoleTags": [],
      "requiredTeamRoleTags": [],
      "reasonRequired": false
    }

    Usage: cortex verifications periods create -f period.json
    """
    client = ctx.obj["client"]
    r = client.post("api/v1/verification-periods", data=file_input.read(), content_type="application/json")
    print_output_with_context(ctx, r)


@app.command()
def update(
    ctx: typer.Context,
    period_cid: PeriodsCommandOptions.period_cid = ...,
    file_input: Annotated[
        typer.FileText,
        typer.Option("--file", "-f", help="File containing JSON body of the verification period; can be passed as stdin with -, example: -f-"),
    ] = None,
):
    """
    Update a verification period (full replacement)
    """
    client = ctx.obj["client"]
    r = client.put(f"api/v1/verification-periods/{period_cid}", data=file_input.read(), content_type="application/json")
    print_output_with_context(ctx, r)


@app.command()
def delete(
    ctx: typer.Context,
    period_cid: PeriodsCommandOptions.period_cid = ...,
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
):
    """
    Delete a verification period (permanent)
    """
    client = ctx.obj["client"]

    if not force:
        typer.confirm(
            f"Permanently delete verification period '{period_cid}'? This cannot be undone.",
            abort=True,
        )

    client.delete(f"api/v1/verification-periods/{period_cid}")
