import json
from rich import print_json
import typer
from typing_extensions import Annotated

app = typer.Typer(help="Azure Devops commands", no_args_is_help=True)

@app.command()
def add(
    ctx: typer.Context,
    alias: str = typer.Option(..., "--alias", "-a", help="Alias for this configuration"),
    host: str = typer.Option(None, "--host", "-h", help="Optional host name"),
    is_default: bool = typer.Option(False, "--is-default", "-i", help="If this is the default configuration"),
    organization_slug: str = typer.Option(..., "--organization-slug", "-o", help="Identifier for organization"),
    personal_access_token: str = typer.Option(..., "--pat", "-p", help="Personal Access Token"),
    username: str = typer.Option(..., "--username", "-u", help="Username"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON file containing configurations, if command line options not used; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Add a single configuration
    """

    client = ctx.obj["client"]

    if file_input:
        if alias or is_default or host or organization_slug or personal_access_token or username:
            raise typer.BadParameter("When providing a custom event definition file, do not specify any other custom event attributes")
        data = json.loads("".join([line for line in file_input]))
    else:
        data = {
           "alias": alias,
           "host": host,
           "isDefault": is_default,
           "organizationSlug": organization_slug,
           "personalAccessToken": personal_access_token,
           "username": username
        }       

        # remove any data elements that are None - can only be is_default
        data = {k: v for k, v in data.items() if v is not None}
    
    r = client.post("api/v1/azure-devops/configuration", data=data)
    print_json(data=r)

@app.command()
def add_multiple(
    ctx: typer.Context,
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON file containing configurations; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Add multiple configurations
    """

    client = ctx.obj["client"]

    data = json.loads("".join([line for line in file_input]))

    r = client.put("api/v1/azure-devops/configurations", data=data)
    print_json(data=r)

@app.command()
def delete(
    ctx: typer.Context,
    alias: str = typer.Option(..., "--alias", "-a", help="The alias of the configuration"),
):
    """
    Delete a configuration
    """

    client = ctx.obj["client"]

    r = client.delete("api/v1/azure-devops/configuration/" + alias)
    print_json(data=r)

@app.command()
def delete_all(
    ctx: typer.Context,
):
    """
    Delete all configurations
    """

    client = ctx.obj["client"]

    r = client.delete("api/v1/azure-devops/configurations")
    print_json(data=r)

@app.command()
def get(
    ctx: typer.Context,
    alias: str = typer.Option(..., "--alias", "-a", help="The alias of the configuration"),
):
    """
    Get a configuration
    """

    client = ctx.obj["client"]

    r = client.get("api/v1/azure-devops/configuration/" + alias)
    print_json(data=r)

@app.command()
def list(
    ctx: typer.Context,
):
    """
    Get all configurations
    """

    client = ctx.obj["client"]

    r = client.get("api/v1/azure-devops/configurations")
    print_json(data=r)

@app.command()
def get_default(
    ctx: typer.Context,
):
    """
    Get default configuration
    """

    client = ctx.obj["client"]

    r = client.get("api/v1/azure-devops/default-configuration")
    print_json(data=r)


@app.command()
def update(
    ctx: typer.Context,
    alias: str = typer.Option(..., "--alias", "-a", help="The alias of the configuration"),
    is_default: bool = typer.Option(False, "--is-default", "-i", help="If this is the default configuration"),
):
    """
    Update a configuration
    """

    client = ctx.obj["client"]

    data = {
       "alias": alias,
       "isDefault": is_default
    }

    r = client.put("api/v1/azure-devops/configuration/" + alias, data=data)
    print_json(data=r)

@app.command()
def validate(
    ctx: typer.Context,
    alias: str = typer.Option(..., "--alias", "-a", help="The alias of the configuration"),
):
    """
    Validate a configuration
    """

    client = ctx.obj["client"]

    r = client.post("api/v1/azure-devops/configurations/validate" + alias)
    print_json(data=r)

@app.command()
def validate_all(
    ctx: typer.Context,
):
    """
    Validate all configurations
    """

    client = ctx.obj["client"]

    r = client.post("api/v1/azure-devops/configurations")
    print_json(data=r)
