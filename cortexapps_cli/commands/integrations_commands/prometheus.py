import json
from rich import print_json
import typer
from typing_extensions import Annotated

app = typer.Typer(help="Prometheus commands", no_args_is_help=True)

@app.command()
def add(
    ctx: typer.Context,
    alias: str = typer.Option(None,  "--alias", "-a", help="Alias for this configuration"),
    host: str = typer.Option(None, "--host", "-h", help="Optional host name"),
    username: str = typer.Option(None, "--username", "-u", help="username"),
    password: str = typer.Option(None, "--password", "-p", help="password"),
    tenant_id: str = typer.Option(None, "--tenant", "-t", help="Optional tenant id"),
    is_default: bool = typer.Option(False, "--is-default", "-i", help="If this is the default configuration"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON file containing configurations, if command line options not used; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Add a single configuration
    """

    client = ctx.obj["client"]

    if file_input:
        if alias or host or username or password or tenant_id or is_default:
            raise typer.BadParameter("When providing a prometheus definition file, do not specify any other attributes")
        data = json.loads("".join([line for line in file_input]))
    else:
        
        data = {
           "alias": alias,
           "host": host,
           "username": username,
           "password": password,
           "tenant_id": tenant_id,
           "is_default": is_default
        }       

        for k, v in data.items():
            if v is None:
                raise typer.BadParameter("Missing required parameter: " + k)
    
    r = client.post("api/v1/prometheus/configuration", data=data)
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

    r = client.put("api/v1/prometheus/configurations", data=data)
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

    r = client.delete("api/v1/prometheus/configuration/" + alias)
    print_json(data=r)

@app.command()
def delete_all(
    ctx: typer.Context,
):
    """
    Delete all configurations
    """

    client = ctx.obj["client"]

    r = client.delete("api/v1/prometheus/configurations")
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

    r = client.get("api/v1/prometheus/configuration/" + alias)
    print_json(data=r)

@app.command()
def list(
    ctx: typer.Context,
):
    """
    Get all configurations
    """

    client = ctx.obj["client"]

    r = client.get("api/v1/prometheus/configurations")
    print_json(data=r)

@app.command()
def get_default(
    ctx: typer.Context,
):
    """
    Get default configuration
    """

    client = ctx.obj["client"]

    r = client.get("api/v1/prometheus/default-configuration")
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

    r = client.put("api/v1/prometheus/configuration/" + alias, data=data)
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

    r = client.post("api/v1/prometheus/configurations/validate" + alias)
    print_json(data=r)

@app.command()
def validate_all(
    ctx: typer.Context,
):
    """
    Validate all configurations
    """

    client = ctx.obj["client"]

    r = client.post("api/v1/prometheus/configurations")
    print_json(data=r)
