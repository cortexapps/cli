import typer
from typing import Optional
from typing_extensions import Annotated

from cortexapps_cli.command_options import ListCommandOptions
from cortexapps_cli.utils import print_output_with_context

app = typer.Typer(help="Entity-level verification commands", no_args_is_help=True)


class EntityVerificationOptions:
    tag = Annotated[
        str,
        typer.Option("--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity"),
    ]
    period_cid = Annotated[
        str,
        typer.Option("--period-cid", "-p", help="The CID of the verification period"),
    ]
    is_active = Annotated[
        Optional[bool],
        typer.Option("--is-active", "-a", help="Filter to only active or inactive periods", show_default=False),
    ]


@app.command(name="list")
def entity_list(
    ctx: typer.Context,
    tag: EntityVerificationOptions.tag = ...,
    is_active: EntityVerificationOptions.is_active = None,
    table_output: ListCommandOptions.table_output = False,
    csv_output: ListCommandOptions.csv_output = False,
    columns: ListCommandOptions.columns = [],
    no_headers: ListCommandOptions.no_headers = False,
    filters: ListCommandOptions.filters = [],
    sort: ListCommandOptions.sort = [],
):
    """
    List verification periods for a specific entity
    """
    client = ctx.obj["client"]

    if (table_output or csv_output) and not ctx.params.get("columns"):
        ctx.params["columns"] = [
            "Period CID=period.cid",
            "Period Name=period.name",
            "Status=status",
            "Verified At=verifiedAt",
        ]

    params = {"isActive": is_active}
    params = {k: v for k, v in params.items() if v is not None}

    r = client.get(f"api/v1/catalog/{tag}/verifications", params=params)
    print_output_with_context(ctx, r)


@app.command()
def verify(
    ctx: typer.Context,
    tag: EntityVerificationOptions.tag = ...,
    period_cid: EntityVerificationOptions.period_cid = ...,
    status: str = typer.Option(
        ...,
        "--status",
        "-s",
        help="Verification answer: VERIFIED_CORRECT or VERIFIED_INCORRECT",
    ),
    reason: Optional[str] = typer.Option(
        None,
        "--reason",
        "-r",
        help="Optional reason (required when period has reasonRequired=true)",
        show_default=False,
    ),
):
    """
    Verify a single entity in a verification period
    """
    client = ctx.obj["client"]

    data = {"status": status}
    if reason is not None:
        data["reason"] = reason

    r = client.put(f"api/v1/catalog/{tag}/verifications/{period_cid}", data=data)
    print_output_with_context(ctx, r)
