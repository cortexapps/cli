import json
from rich import print_json
import typer
from typing_extensions import Annotated

app = typer.Typer(help="Dynatrace commands", no_args_is_help=True)

@app.command()
def add(
    ctx: typer.Context,
    api_key: str = typer.Option(None, "--api-key", "-api", help="API key"),
    domain: str = typer.Option(None, "--domain", "-d", help="Domain"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON file containing configuration, if command line options not used; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Add a configuration
    """
    client = ctx.obj["client"]

    if file_input:
        if api_key or domain:
            raise typer.BadParameter("When providing a configuration file, do not specify any other attributes")
        data = json.loads("".join([line for line in file_input]))
    else:
        data = {
           "apiKey": api_key,
           "domain": domain,
        }
        data = {k: v for k, v in data.items() if v is not None}

    r = client.post("api/v1/dynatrace/configuration", data=data)
    print_json(data=r)

@app.command()
def get(ctx: typer.Context):
    """
    Get the configuration
    """
    client = ctx.obj["client"]
    r = client.get("api/v1/dynatrace/default-configuration")
    print_json(data=r)

@app.command()
def update(
    ctx: typer.Context,
    api_key: str = typer.Option(None, "--api-key", "-api", help="API key"),
    domain: str = typer.Option(None, "--domain", "-d", help="Domain"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON file containing configuration, if command line options not used; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Update the configuration
    """
    client = ctx.obj["client"]

    if file_input:
        if api_key or domain:
            raise typer.BadParameter("When providing a configuration file, do not specify any other attributes")
        data = json.loads("".join([line for line in file_input]))
    else:
        data = {
           "apiKey": api_key,
           "domain": domain,
        }
        data = {k: v for k, v in data.items() if v is not None}

    r = client.put("api/v1/dynatrace/configuration", data=data)
    print_json(data=r)

@app.command()
def validate(ctx: typer.Context):
    """
    Validate the configuration
    """
    client = ctx.obj["client"]
    r = client.post("api/v1/dynatrace/configuration/validate")
    print_json(data=r)

@app.command()
def delete(ctx: typer.Context):
    """
    Delete the configuration
    """
    client = ctx.obj["client"]
    r = client.delete("api/v1/dynatrace/configurations")
    print_json(data=r)
