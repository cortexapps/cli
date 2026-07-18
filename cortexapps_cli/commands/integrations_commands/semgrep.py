import json
from rich import print_json
import typer
from typing_extensions import Annotated

app = typer.Typer(help="Semgrep commands", no_args_is_help=True)

@app.command()
def add(
    ctx: typer.Context,
    alias: str = typer.Option(..., "--alias", "-a", help="Alias for this configuration"),
    api_key: str = typer.Option(..., "--api-key", "-api", help="API key"),
    is_default: bool = typer.Option(False, "--is-default", "-i", help="If this is the default configuration"),
    organization_id: str = typer.Option(..., "--organization-id", "-oi", help="Organization ID"),
    organization_slug: str = typer.Option(..., "--organization-slug", "-os", help="Organization slug"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON file containing configurations, if command line options not used; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Add a single configuration
    """

    client = ctx.obj["client"]

    if file_input:
        if alias or api_key or is_default or organization_id or organization_slug:
            raise typer.BadParameter("When providing a configuration file, do not specify any other attributes")
        data = json.loads("".join([line for line in file_input]))
    else:
        data = {
           "alias": alias,
           "apiKey": api_key,
           "isDefault": is_default,
           "organizationId": organization_id,
           "organizationSlug": organization_slug,
        }

        # remove any data elements that are None
        data = {k: v for k, v in data.items() if v is not None}

    r = client.post("api/v1/semgrep/configuration", data=data)
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

    r = client.post("api/v1/semgrep/configurations", data=data)
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

    r = client.delete("api/v1/semgrep/configuration/" + alias)
    print_json(data=r)

@app.command()
def delete_all(
    ctx: typer.Context,
):
    """
    Delete all configurations
    """

    client = ctx.obj["client"]

    r = client.delete("api/v1/semgrep/configurations")
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

    r = client.get("api/v1/semgrep/configuration/" + alias)
    print_json(data=r)

@app.command()
def list(
    ctx: typer.Context,
):
    """
    Get all configurations
    """

    client = ctx.obj["client"]

    r = client.get("api/v1/semgrep/configurations")
    print_json(data=r)

@app.command()
def get_default(
    ctx: typer.Context,
):
    """
    Get default configuration
    """

    client = ctx.obj["client"]

    r = client.get("api/v1/semgrep/default-configuration")
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

    r = client.put("api/v1/semgrep/configuration/" + alias, data=data)
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

    r = client.post("api/v1/semgrep/configuration/validate/" + alias)
    print_json(data=r)

@app.command()
def validate_all(
    ctx: typer.Context,
):
    """
    Validate all configurations
    """

    client = ctx.obj["client"]

    r = client.post("api/v1/semgrep/configuration/validate")
    print_json(data=r)
