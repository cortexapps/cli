from datetime import datetime
import typer
import json
from enum import Enum
from typing_extensions import Annotated
from cortexapps_cli.utils import print_output_with_context

app = typer.Typer(help="API Keys commands")

class DefaultRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    READ_ONLY = "READ_ONLY"

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
        data = {
           "roles": [],
           "name": name
        }

        for role in default_roles.split(","):
            data["roles"].append({"role": role, "type": "DEFAULT"})
        for role in custom_roles.split(","):
            data["roles"].append({"tag": role, "type": "CUSTOM"})

        if description:
            data["description"] = description
        if expiration_date:
            data["expirationDate"] = expiration_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')

    r = client.post("api/v1/auth/key", data=data)
    #print(r)
    print_output_with_context(ctx, r)
