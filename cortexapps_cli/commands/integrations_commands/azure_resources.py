import json
from rich import print_json
import typer
from typing_extensions import Annotated

app = typer.Typer(help="Azure Resources commands", no_args_is_help=True)

# Make this a common client function?

# Need a helper function to parse custom_data.
# cannot do this in type: list[Tuple[str, str]] | None  = typer.Option(None)
# Results in: 
# AssertionError: List types with complex sub-types are not currently supported
#
# borrowed from https://github.com/fastapi/typer/issues/387
def _parse_key_value(values):
    if values is None:
        return []
    result = []
    for value in values:
        a, r = value.split('=')
        result.append({"accountId": a, "role": r})
    return result

def _parse_key_value_types(values):
    if values is None:
        return []
    result = []
    for value in values:
        a, r = value.split('=')
        result.append({"type": a, "enabled": r})
    return result

@app.command()
def add(
    ctx: typer.Context,
    alias: str = typer.Option(..., "--alias", "-a", help="Alias for this configuration"),
    is_default: bool = typer.Option(False, "--is-default", "-i", help="If this is the default configuration"),
    host: str = typer.Option(None, "--host", "-h", help="Optional host name"),
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
    
    r = client.post("api/v1/azure-resources/configuration", data=data)
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

    r = client.put("api/v1/azure-resources/configurations", data=data)
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

    r = client.delete("api/v1/azure-resources/configuration/" + alias)
    print_json(data=r)

@app.command()
def delete_all(
    ctx: typer.Context,
):
    """
    Delete all configurations
    """

    client = ctx.obj["client"]

    r = client.delete("api/v1/azure-resources/configurations")
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

    r = client.get("api/v1/azure-resources/configuration/" + alias)
    print_json(data=r)

@app.command("list")
def azure_resources_list(
    ctx: typer.Context,
):
    """
    Get all configurations
    """

    client = ctx.obj["client"]

    r = client.get("api/v1/azure-resources/configurations")
    print_json(data=r)

@app.command()
def get_default(
    ctx: typer.Context,
):
    """
    Get default configuration
    """

    client = ctx.obj["client"]

    r = client.get("api/v1/azure-resources/default-configuration")
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

    r = client.put("api/v1/azure-resources/configuration/" + alias, data=data)
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

    r = client.post("api/v1/azure-resources/configurations/validate" + alias)
    print_json(data=r)

@app.command()
def validate_all(
    ctx: typer.Context,
):
    """
    Validate all configurations
    """

    client = ctx.obj["client"]

    r = client.post("api/v1/azure-resources/configurations")
    print_json(data=r)

@app.command()
def list_types(
    ctx: typer.Context,
    include_disabled: bool = typer.Option(False, "--include-disabled", "-i", help="When true, includes all types supported"),
    page: int | None = typer.Option(None, "--page", "-p", help="Page number to return, 0 indexed - omit to fetch all pages"),
    page_size: int | None = typer.Option(None, "--page-size", "-z", help="Page size for results")
):
    """
    List AWS types that have been imported
    """

    client = ctx.obj["client"]

    params = {
        "includeDisabled": include_disabled,
        "page": page,
        "pageSize": page_size
    }

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    r = client.get("api/v1/azure-resources/types", params=params)
    print_json(data=r)

@app.command()
def update_types(
    ctx: typer.Context,
    types: list[str] | None  = typer.Option(None, "--types", "-t", callback=_parse_key_value_types, help="List of type=True|False pairs (only if file input not provided."),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON File containing types that should be discovered and imported into catalog; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Update configured Azure Resources types
    """

    client = ctx.obj["client"]

    data = {
       "types": []
    }
    series_data = {
       "types": types
    }

    if file_input:
        data = json.loads("".join([line for line in file_input]))
    else:
        if not types:
            raise typer.BadParameter("One of --types or --file must be provided.")

    if types:
        for item in types:
           data["types"].append(item)

    print(data)
    r = client.put("api/v1/azure-resources/types", data=data)
    print_json(data=r)
