import json
from enum import Enum
from rich import print_json
import typer
from typing_extensions import Annotated

class Region(str, Enum):
    USA = "USA"
    US2 = "US2"
    EU = "EU"
    AUS = "AUS"

app = typer.Typer(help="Snyk commands", no_args_is_help=True)

@app.command()
def add(
    ctx: typer.Context,
    auth_token: str = typer.Option(None, "--auth-token", "-at", help="Auth token"),
    region: Region = typer.Option(None, "--region", "-r", help="Region"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON file containing configuration, if command line options not used; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Add a configuration
    """
    client = ctx.obj["client"]

    if file_input:
        if auth_token or region:
            raise typer.BadParameter("When providing a configuration file, do not specify any other attributes")
        data = json.loads("".join([line for line in file_input]))
    else:
        data = {
           "authToken": auth_token,
           "region": region.value if region else None,
        }
        data = {k: v for k, v in data.items() if v is not None}

    r = client.post("api/v1/snyk/configuration", data=data)
    print_json(data=r)

@app.command()
def get(ctx: typer.Context):
    """
    Get the configuration
    """
    client = ctx.obj["client"]
    r = client.get("api/v1/snyk/default-configuration")
    print_json(data=r)

@app.command()
def update(
    ctx: typer.Context,
    auth_token: str = typer.Option(None, "--auth-token", "-at", help="Auth token"),
    region: Region = typer.Option(None, "--region", "-r", help="Region"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON file containing configuration, if command line options not used; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Update the configuration
    """
    client = ctx.obj["client"]

    if file_input:
        if auth_token or region:
            raise typer.BadParameter("When providing a configuration file, do not specify any other attributes")
        data = json.loads("".join([line for line in file_input]))
    else:
        data = {
           "authToken": auth_token,
           "region": region.value if region else None,
        }
        data = {k: v for k, v in data.items() if v is not None}

    r = client.put("api/v1/snyk/configuration", data=data)
    print_json(data=r)

@app.command()
def validate(ctx: typer.Context):
    """
    Validate the configuration
    """
    client = ctx.obj["client"]
    r = client.post("api/v1/snyk/configuration/validate")
    print_json(data=r)

@app.command()
def delete(ctx: typer.Context):
    """
    Delete the configuration
    """
    client = ctx.obj["client"]
    r = client.delete("api/v1/snyk/configurations")
    print_json(data=r)
