import json
from rich import print_json
import typer
from typing_extensions import Annotated

app = typer.Typer(help="Sentry commands", no_args_is_help=True)

@app.command()
def add(
    ctx: typer.Context,
    auth_token: str = typer.Option(None, "--auth-token", "-at", help="Auth token"),
    organization_slug: str = typer.Option(None, "--organization-slug", "-o", help="Organization slug"),
    host: str = typer.Option(None, "--host", "-h", help="Host"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON file containing configuration, if command line options not used; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Add a configuration
    """
    client = ctx.obj["client"]

    if file_input:
        if auth_token or organization_slug or host:
            raise typer.BadParameter("When providing a configuration file, do not specify any other attributes")
        data = json.loads("".join([line for line in file_input]))
    else:
        data = {
           "authToken": auth_token,
           "organizationSlug": organization_slug,
           "host": host,
        }
        data = {k: v for k, v in data.items() if v is not None}

    r = client.post("api/v1/sentry/configuration", data=data)
    print_json(data=r)

@app.command()
def get(ctx: typer.Context):
    """
    Get the configuration
    """
    client = ctx.obj["client"]
    r = client.get("api/v1/sentry/default-configuration")
    print_json(data=r)

@app.command()
def update(
    ctx: typer.Context,
    auth_token: str = typer.Option(None, "--auth-token", "-at", help="Auth token"),
    organization_slug: str = typer.Option(None, "--organization-slug", "-o", help="Organization slug"),
    host: str = typer.Option(None, "--host", "-h", help="Host"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON file containing configuration, if command line options not used; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Update the configuration
    """
    client = ctx.obj["client"]

    if file_input:
        if auth_token or organization_slug or host:
            raise typer.BadParameter("When providing a configuration file, do not specify any other attributes")
        data = json.loads("".join([line for line in file_input]))
    else:
        data = {
           "authToken": auth_token,
           "organizationSlug": organization_slug,
           "host": host,
        }
        data = {k: v for k, v in data.items() if v is not None}

    r = client.put("api/v1/sentry/configuration", data=data)
    print_json(data=r)

@app.command()
def validate(ctx: typer.Context):
    """
    Validate the configuration
    """
    client = ctx.obj["client"]
    r = client.post("api/v1/sentry/configuration/validate")
    print_json(data=r)

@app.command()
def delete(ctx: typer.Context):
    """
    Delete the configuration
    """
    client = ctx.obj["client"]
    r = client.delete("api/v1/sentry/configurations")
    print_json(data=r)
