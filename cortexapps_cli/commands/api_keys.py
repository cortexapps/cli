from datetime import datetime
import typer
import json
from enum import Enum
from typing_extensions import Annotated
from cortexapps_cli.utils import print_output_with_context
from cortexapps_cli.command_options import CommandOptions
from cortexapps_cli.command_options import ListCommandOptions

app = typer.Typer(
    help="API Keys commands",
    no_args_is_help=True
)

class DefaultRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    READ_ONLY = "READ_ONLY"

@app.command()
def list(
    ctx: typer.Context,
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
    List API keys. The API key used to make the request must have the Edit API keys permission.
    """

    client = ctx.obj["client"]

    params = {
       "page": page,
       "pageSize": page_size
    }       

    if (table_output or csv_output) and not ctx.params.get('columns'):
        ctx.params['columns'] = [
            "CID=cid",
            "Name=name",
            "Last4=last4",
            "Description=description",
            "Roles=roles",
            "CreatedDate=createdDate",
            "ExpirationDate=expirationDate",
        ]

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}
    
    if page is None:
        r = client.fetch("api/v1/auth/key", params=params)
    else:
        r = client.get("api/v1/auth/key", params=params)
    print_output_with_context(ctx, r)

@app.command()
def create(
    ctx: typer.Context,
    description: str | None = typer.Option(None, "--description", "-d", help="Description of the API key"),
    name: str | None = typer.Option(None, "--name", "-n", help="Name of the API key"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help=" File containing content; can be passed as stdin with -, example: -f-")] = None,
    default_roles: str | None  = typer.Option(None, "--default-roles", "-dr", help="Comma-separated list of default roles (only if file input not provided."),
    custom_roles: str | None  = typer.Option(None, "--custom-roles", "-cr", help="Comma-separated list of custom roles (only if file input not provided."),
    expiration_date: datetime | None = typer.Option(None, "--expiration-date", "-e", help="Expiration date of the API key", formats=["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"]),
):
    """
    Create new API key.  The API key used to make the request must have the Create API keys permission
    """
    client = ctx.obj["client"]

    if file_input:
        if name or description or expiration_date or default_roles or custom_roles:
            raise typer.BadParameter("When providing an API definition file, do not specify any other attributes")
        data = json.loads("".join([line for line in file_input]))
    else:
        if not default_roles and not custom_roles:
            raise typer.BadParameter("One of default-roles or custom-roles is required")

        data = {
           "roles": [],
           "name": name
        }

        if default_roles is not None:
            for role in default_roles.split(","):
                data["roles"].append({"role": role, "type": "DEFAULT"})
        if custom_roles is not None:
            for role in custom_roles.split(","):
                data["roles"].append({"tag": role, "type": "CUSTOM"})

        if description:
            data["description"] = description
        if expiration_date:
            data["expirationDate"] = expiration_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')

    r = client.post("api/v1/auth/key", data=data)
    print_output_with_context(ctx, r)

@app.command()
def update(
    ctx: typer.Context,
    cid: str = typer.Option(..., "--cid", "-c", help="The unique, auto-generated identifier for the API key"),
    description: str | None = typer.Option(None, "--description", "-d", help="Description of the API key"),
    name: str = typer.Option(..., "--name", "-n", help="Name of the API key"),
):
    """
    Update API key.  The API key used to make the request must have the Edit API keys permission.
    """
    client = ctx.obj["client"]

    data = {
       "name": name
    }
    if description is not None:
        data["description"] = description

    r = client.put("api/v1/auth/key/" + cid, data=data)
    print_output_with_context(ctx, r)

@app.command()
def get(
    ctx: typer.Context,
    cid: str = typer.Option(..., "--cid", "-c", help="The unique, auto-generated identifier for the API key"),
):
    """
    Get API key.
    """

    client = ctx.obj["client"]
    
    r = client.get("api/v1/auth/key/"+ cid)
    print_output_with_context(ctx, r)

@app.command()
def delete(
    ctx: typer.Context,
    cid: str = typer.Option(..., "--cid", "-c", help="The unique, auto-generated identifier for the API key"),
):
    """
    Delete API key.
    """

    client = ctx.obj["client"]
    
    r = client.delete("api/v1/auth/key/"+ cid)
