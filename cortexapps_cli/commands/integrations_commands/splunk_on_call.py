import json
from rich import print_json
import typer
from typing_extensions import Annotated

app = typer.Typer(help="Splunk On Call commands", no_args_is_help=True)

@app.command()
def add(
    ctx: typer.Context,
    api_id: str = typer.Option(None, "--api-id", "-ai", help="API ID"),
    api_key: str = typer.Option(None, "--api-key", "-api", help="API key"),
    organization: str = typer.Option(None, "--organization", "-o", help="Organization"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON file containing configuration, if command line options not used; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Add a configuration
    """
    client = ctx.obj["client"]

    if file_input:
        if api_id or api_key or organization:
            raise typer.BadParameter("When providing a configuration file, do not specify any other attributes")
        data = json.loads("".join([line for line in file_input]))
    else:
        data = {
           "apiId": api_id,
           "apiKey": api_key,
           "organization": organization,
        }
        data = {k: v for k, v in data.items() if v is not None}

    r = client.post("api/v1/victorops/configuration", data=data)
    print_json(data=r)

@app.command()
def get(ctx: typer.Context):
    """
    Get the configuration
    """
    client = ctx.obj["client"]
    r = client.get("api/v1/victorops/default-configuration")
    print_json(data=r)

@app.command()
def update(
    ctx: typer.Context,
    api_id: str = typer.Option(None, "--api-id", "-ai", help="API ID"),
    api_key: str = typer.Option(None, "--api-key", "-api", help="API key"),
    organization: str = typer.Option(None, "--organization", "-o", help="Organization"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON file containing configuration, if command line options not used; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Update the configuration
    """
    client = ctx.obj["client"]

    if file_input:
        if api_id or api_key or organization:
            raise typer.BadParameter("When providing a configuration file, do not specify any other attributes")
        data = json.loads("".join([line for line in file_input]))
    else:
        data = {
           "apiId": api_id,
           "apiKey": api_key,
           "organization": organization,
        }
        data = {k: v for k, v in data.items() if v is not None}

    r = client.put("api/v1/victorops/configuration", data=data)
    print_json(data=r)

@app.command()
def validate(ctx: typer.Context):
    """
    Validate the configuration
    """
    client = ctx.obj["client"]
    r = client.post("api/v1/victorops/configuration/validate")
    print_json(data=r)

@app.command()
def delete(ctx: typer.Context):
    """
    Delete the configuration
    """
    client = ctx.obj["client"]
    r = client.delete("api/v1/victorops/configurations")
    print_json(data=r)
