from enum import Enum
import json
from rich import print_json
import typer
from typing_extensions import Annotated
from cortexapps_cli.command_options import ListCommandOptions
from cortexapps_cli.utils import print_output_with_context

app = typer.Typer(help="New Relic commands", no_args_is_help=True)

class Region(str, Enum):
    US = "US"
    EU = "EU"

@app.command(no_args_is_help=True)
def add(
    ctx: typer.Context,
    alias: str = typer.Option(None, "--alias", "-a", help="Alias for this configuration"),
    account_id: str = typer.Option(None, "--account-id", "-acc", help="New Relic account ID"),
    personal_key: str = typer.Option(None, "--personal-key", "-pk", help="New Relic personal API key"),
    region: Region = typer.Option(Region.US, "--region", "-r", help="Region (US or EU)"),
    is_default: bool = typer.Option(False, "--is-default", "-i", help="If this is the default configuration"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON file containing configurations, if command line options not used; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Add a single configuration
    """

    client = ctx.obj["client"]

    if file_input:
        if alias or account_id or personal_key:
            raise typer.BadParameter("When providing a file, do not specify --alias, --account-id, or --personal-key")
        data = json.loads("".join([line for line in file_input]))
    else:
        if not alias or not account_id or not personal_key:
            raise typer.BadParameter("--alias, --account-id, and --personal-key are required when not using --file")
        if not personal_key.startswith("NRAK"):
            raise typer.BadParameter("--personal-key must start with 'NRAK'")
        data = {
           "alias": alias,
           "accountId": account_id,
           "personalKey": personal_key,
           "region": region.value,
           "isDefault": is_default,
        }

    r = client.post("api/v1/newrelic/configuration", data=data)
    print_json(data=r)

@app.command(no_args_is_help=True)
def add_multiple(
    ctx: typer.Context,
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON file containing configurations; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Add multiple configurations

    JSON file format:
    \b
    {
      "configurations": [
        {
          "accountId": 1,
          "alias": "text",
          "isDefault": true,
          "personalKey": "text",
          "region": "US"
        }
      ]
    }
    """

    client = ctx.obj["client"]

    data = json.loads("".join([line for line in file_input]))

    r = client.post("api/v1/newrelic/configurations", data=data)
    print_json(data=r)

@app.command(no_args_is_help=True)
def delete(
    ctx: typer.Context,
    alias: str = typer.Option(..., "--alias", "-a", help="The alias of the configuration"),
):
    """
    Delete a configuration
    """

    client = ctx.obj["client"]

    r = client.delete("api/v1/newrelic/configuration/" + alias)
    print_json(data=r)

@app.command()
def delete_all(
    ctx: typer.Context,
):
    """
    Delete all configurations
    """

    client = ctx.obj["client"]

    r = client.delete("api/v1/newrelic/configurations")
    print_json(data=r)

@app.command(no_args_is_help=True)
def get(
    ctx: typer.Context,
    alias: str = typer.Option(..., "--alias", "-a", help="The alias of the configuration"),
):
    """
    Get a configuration
    """

    client = ctx.obj["client"]

    r = client.get("api/v1/newrelic/configuration/" + alias)
    print_json(data=r)

@app.command()
def list(
    ctx: typer.Context,
    table_output: ListCommandOptions.table_output = False,
    csv_output: ListCommandOptions.csv_output = False,
    columns: ListCommandOptions.columns = [],
    no_headers: ListCommandOptions.no_headers = False,
    filters: ListCommandOptions.filters = [],
    sort: ListCommandOptions.sort = [],
):
    """
    Get all configurations
    """

    client = ctx.obj["client"]

    if (table_output or csv_output) and not ctx.params.get('columns'):
        ctx.params['columns'] = [
            "Alias=alias",
            "AccountId=accountId",
            "Region=region",
            "IsDefault=isDefault",
        ]

    r = client.get("api/v1/newrelic/configurations")
    print_output_with_context(ctx, r)

@app.command()
def get_default(
    ctx: typer.Context,
):
    """
    Get default configuration
    """

    client = ctx.obj["client"]

    r = client.get("api/v1/newrelic/default-configuration")
    print_json(data=r)


@app.command(no_args_is_help=True)
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

    r = client.put("api/v1/newrelic/configuration/" + alias, data=data)
    print_json(data=r)

@app.command(no_args_is_help=True)
def validate(
    ctx: typer.Context,
    alias: str = typer.Option(..., "--alias", "-a", help="The alias of the configuration"),
):
    """
    Validate a configuration
    """

    client = ctx.obj["client"]

    r = client.post("api/v1/newrelic/configuration/validate/" + alias)
    print_json(data=r)

@app.command()
def validate_all(
    ctx: typer.Context,
):
    """
    Validate all configurations
    """

    client = ctx.obj["client"]

    r = client.post("api/v1/newrelic/configuration/validate")
    print_json(data=r)
