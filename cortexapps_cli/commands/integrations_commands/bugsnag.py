import json
from rich import print_json
import typer
from typing_extensions import Annotated

app = typer.Typer(help="Bugsnag commands", no_args_is_help=True)

@app.command()
def add(
    ctx: typer.Context,
    auth_token: str = typer.Option(None, "--auth-token", "-at", help="Auth token"),
    organization_id: str = typer.Option(None, "--organization-id", "-o", help="Organization ID"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON file containing configuration, if command line options not used; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Add a configuration
    """
    client = ctx.obj["client"]

    if file_input:
        if auth_token or organization_id:
            raise typer.BadParameter("When providing a configuration file, do not specify any other attributes")
        data = json.loads("".join([line for line in file_input]))
    else:
        data = {
           "authToken": auth_token,
           "organizationId": organization_id,
        }
        data = {k: v for k, v in data.items() if v is not None}

    r = client.post("api/v1/bugsnag/configuration", data=data)
    print_json(data=r)

@app.command()
def get(ctx: typer.Context):
    """
    Get the configuration
    """
    client = ctx.obj["client"]
    r = client.get("api/v1/bugsnag/default-configuration")
    print_json(data=r)

@app.command()
def update(
    ctx: typer.Context,
    auth_token: str = typer.Option(None, "--auth-token", "-at", help="Auth token"),
    organization_id: str = typer.Option(None, "--organization-id", "-o", help="Organization ID"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON file containing configuration, if command line options not used; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Update the configuration
    """
    client = ctx.obj["client"]

    if file_input:
        if auth_token or organization_id:
            raise typer.BadParameter("When providing a configuration file, do not specify any other attributes")
        data = json.loads("".join([line for line in file_input]))
    else:
        data = {
           "authToken": auth_token,
           "organizationId": organization_id,
        }
        data = {k: v for k, v in data.items() if v is not None}

    r = client.put("api/v1/bugsnag/configuration", data=data)
    print_json(data=r)

@app.command()
def validate(ctx: typer.Context):
    """
    Validate the configuration
    """
    client = ctx.obj["client"]
    r = client.post("api/v1/bugsnag/configuration/validate")
    print_json(data=r)

@app.command()
def delete(ctx: typer.Context):
    """
    Delete the configuration
    """
    client = ctx.obj["client"]
    r = client.delete("api/v1/bugsnag/configurations")
    print_json(data=r)
