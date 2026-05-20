import json
from rich import print_json
import typer
from typing_extensions import Annotated

app = typer.Typer(help="xMatters commands", no_args_is_help=True)

@app.command()
def add(
    ctx: typer.Context,
    organization_slug: str = typer.Option(None, "--organization-slug", "-o", help="Organization slug"),
    password: str = typer.Option(None, "--password", "-p", help="Password"),
    username: str = typer.Option(None, "--username", "-u", help="Username"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON file containing configuration, if command line options not used; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Add a configuration
    """
    client = ctx.obj["client"]

    if file_input:
        if organization_slug or password or username:
            raise typer.BadParameter("When providing a configuration file, do not specify any other attributes")
        data = json.loads("".join([line for line in file_input]))
    else:
        data = {
           "organizationSlug": organization_slug,
           "password": password,
           "username": username,
        }
        data = {k: v for k, v in data.items() if v is not None}

    r = client.post("api/v1/xmatters/configuration", data=data)
    print_json(data=r)

@app.command()
def get(ctx: typer.Context):
    """
    Get the configuration
    """
    client = ctx.obj["client"]
    r = client.get("api/v1/xmatters/default-configuration")
    print_json(data=r)

@app.command()
def update(
    ctx: typer.Context,
    organization_slug: str = typer.Option(None, "--organization-slug", "-o", help="Organization slug"),
    password: str = typer.Option(None, "--password", "-p", help="Password"),
    username: str = typer.Option(None, "--username", "-u", help="Username"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON file containing configuration, if command line options not used; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Update the configuration
    """
    client = ctx.obj["client"]

    if file_input:
        if organization_slug or password or username:
            raise typer.BadParameter("When providing a configuration file, do not specify any other attributes")
        data = json.loads("".join([line for line in file_input]))
    else:
        data = {
           "organizationSlug": organization_slug,
           "password": password,
           "username": username,
        }
        data = {k: v for k, v in data.items() if v is not None}

    r = client.put("api/v1/xmatters/configuration", data=data)
    print_json(data=r)

@app.command()
def validate(ctx: typer.Context):
    """
    Validate the configuration
    """
    client = ctx.obj["client"]
    r = client.post("api/v1/xmatters/configuration/validate")
    print_json(data=r)

@app.command()
def delete(ctx: typer.Context):
    """
    Delete the configuration
    """
    client = ctx.obj["client"]
    r = client.delete("api/v1/xmatters/configurations")
    print_json(data=r)
