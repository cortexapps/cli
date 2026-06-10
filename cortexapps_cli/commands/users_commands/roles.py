from typing import List, Optional
import typer
from cortexapps_cli.command_options import ListCommandOptions
from cortexapps_cli.utils import print_output_with_context

app = typer.Typer(help="Roles commands", no_args_is_help=True)

@app.command()
def list(
    ctx: typer.Context,
    email: Optional[List[str]] = typer.Option(None, "--email", "-e", help="Filter by email address; can be specified multiple times", show_default=False),
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
    List user role assignments. The API key used to make the request must have the View Roles permission.
    """

    client = ctx.obj["client"]

    params = {
        "page": page,
        "pageSize": page_size,
    }

    if email:
        params["email"] = ",".join(email)

    if (table_output or csv_output) and not ctx.params.get('columns'):
        ctx.params['columns'] = [
            "Email=email",
            "Name=name",
            "Roles=roles",
        ]

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    if page is None:
        r = client.fetch("api/v1/users/roles", params=params)
    else:
        r = client.get("api/v1/users/roles", params=params)
    print_output_with_context(ctx, r)
