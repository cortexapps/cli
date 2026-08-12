import json
from rich import print_json
import typer
from typing_extensions import Annotated

app = typer.Typer(help="Harness commands", no_args_is_help=True)


@app.command()
def add(
    ctx: typer.Context,
    alias: str = typer.Option(..., "--alias", "-a", help="Alias for this configuration"),
    api_key: str = typer.Option(..., "--api-key", "-k", help="Harness API key"),
    account_id: str = typer.Option(..., "--account-id", "-id", help="Harness account ID"),
    host: str = typer.Option(None, "--host", "-h", help="Harness host URL (optional; defaults to https://app.harness.io)"),
    is_default: bool = typer.Option(False, "--is-default", "-i", help="Set as the default configuration"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON file containing configuration; use - for stdin")] = None,
):
    """
    Add a Harness configuration
    """
    client = ctx.obj["client"]

    if file_input:
        if alias or api_key or account_id or host or is_default:
            raise typer.BadParameter("When providing a configuration file, do not specify any other attributes")
        data = json.loads("".join([line for line in file_input]))
    else:
        data = {
            "alias": alias,
            "apiKey": api_key,
            "accountId": account_id,
            "isDefault": is_default,
        }
        if host is not None:
            data["host"] = host

    r = client.post("api/v1/harness/configuration", data=data)
    print_json(data=r)


@app.command()
def get(
    ctx: typer.Context,
    alias: str = typer.Option(..., "--alias", "-a", help="Alias of the configuration to retrieve"),
):
    """
    Get a single Harness configuration by alias
    """
    client = ctx.obj["client"]
    r = client.get(f"api/v1/harness/configuration/{alias}")
    print_json(data=r)


@app.command()
def list(
    ctx: typer.Context,
):
    """
    List all Harness configurations
    """
    client = ctx.obj["client"]
    r = client.get("api/v1/harness/configurations")
    print_json(data=r)


@app.command()
def get_default(
    ctx: typer.Context,
):
    """
    Get the default Harness configuration
    """
    client = ctx.obj["client"]
    r = client.get("api/v1/harness/default-configuration")
    print_json(data=r)


@app.command()
def update(
    ctx: typer.Context,
    alias: str = typer.Option(..., "--alias", "-a", help="Alias of the configuration to update"),
    api_key: str = typer.Option(None, "--api-key", "-k", help="New Harness API key"),
    account_id: str = typer.Option(None, "--account-id", "-id", help="New Harness account ID"),
    host: str = typer.Option(None, "--host", "-h", help="New Harness host URL"),
    is_default: bool = typer.Option(None, "--is-default", "-i", help="Set as the default configuration"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON file containing update fields; use - for stdin")] = None,
):
    """
    Update a Harness configuration
    """
    client = ctx.obj["client"]

    if file_input:
        if alias or api_key or account_id or host or is_default is not None:
            raise typer.BadParameter("When providing a configuration file, do not specify any other attributes")
        data = json.loads("".join([line for line in file_input]))
    else:
        data = {}
        if api_key is not None:
            data["apiKey"] = api_key
        if account_id is not None:
            data["accountId"] = account_id
        if host is not None:
            data["host"] = host
        if is_default is not None:
            data["isDefault"] = is_default

    r = client.put(f"api/v1/harness/configuration/{alias}", data=data)
    print_json(data=r)


@app.command()
def delete(
    ctx: typer.Context,
    alias: str = typer.Option(..., "--alias", "-a", help="Alias of the configuration to delete"),
):
    """
    Delete a single Harness configuration
    """
    client = ctx.obj["client"]
    r = client.delete(f"api/v1/harness/configuration/{alias}")
    print_json(data=r)


@app.command()
def delete_all(
    ctx: typer.Context,
):
    """
    Delete all Harness configurations
    """
    client = ctx.obj["client"]
    r = client.delete("api/v1/harness/configurations")
    print_json(data=r)


@app.command()
def validate(
    ctx: typer.Context,
    alias: str = typer.Option(..., "--alias", "-a", help="Alias of the configuration to validate"),
):
    """
    Validate a single Harness configuration
    """
    client = ctx.obj["client"]
    r = client.post(f"api/v1/harness/configuration/validate/{alias}")
    print_json(data=r)


@app.command()
def validate_all(
    ctx: typer.Context,
):
    """
    Validate all Harness configurations
    """
    client = ctx.obj["client"]
    r = client.post("api/v1/harness/configuration/validate")
    print_json(data=r)
