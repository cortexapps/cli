import typer
from typing import Optional
from typing_extensions import Annotated

from cortexapps_cli.command_options import ListCommandOptions
from cortexapps_cli.utils import print_output_with_context

import cortexapps_cli.commands.verifications_commands.periods as periods
import cortexapps_cli.commands.verifications_commands.entity as entity

app = typer.Typer(help="Verifications commands", no_args_is_help=True)
app.add_typer(periods.app, name="periods")
app.add_typer(entity.app, name="entity")


class VerificationsCommandOptions:
    period_cid = Annotated[
        Optional[str],
        typer.Option("--period-cid", "-p", help="Filter by verification period CID", show_default=False),
    ]
    status = Annotated[
        Optional[str],
        typer.Option(
            "--status",
            "-s",
            help="Filter by status: PENDING, VERIFIED_CORRECT, or VERIFIED_INCORRECT",
            show_default=False,
        ),
    ]
    is_active = Annotated[
        Optional[bool],
        typer.Option("--is-active", "-a", help="Filter to only active or inactive periods", show_default=False),
    ]


@app.command(name="list")
def verifications_list(
    ctx: typer.Context,
    period_cid: VerificationsCommandOptions.period_cid = None,
    status: VerificationsCommandOptions.status = None,
    is_active: VerificationsCommandOptions.is_active = None,
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
    List verification records
    """
    client = ctx.obj["client"]

    if (table_output or csv_output) and not ctx.params.get("columns"):
        ctx.params["columns"] = [
            "Entity=entity.tag",
            "Period=period.cid",
            "Status=status",
            "Verified At=verifiedAt",
        ]

    params = {
        "periodCid": period_cid,
        "status": status,
        "isActive": is_active,
        "page": page,
        "pageSize": page_size,
    }
    params = {k: v for k, v in params.items() if v is not None}

    if page is None:
        r = client.fetch("api/v1/verifications", params=params)
    else:
        r = client.get("api/v1/verifications", params=params)

    print_output_with_context(ctx, r)


@app.command()
def verify(
    ctx: typer.Context,
    file_input: Annotated[
        typer.FileText,
        typer.Option(
            "--file",
            "-f",
            help="File containing JSON array of verification entries; can be passed as stdin with -, example: -f-",
        ),
    ] = None,
):
    """
    Bulk verify entities. Accepts a JSON array of verification entries.
    HTTP 200 does not guarantee all entries succeeded — check the errors array in the response.
    """
    client = ctx.obj["client"]
    r = client.put("api/v1/verifications", data=file_input.read(), content_type="application/json")
    print_output_with_context(ctx, r)
