import json
from rich import print_json
import typer
from typing_extensions import Annotated

app = typer.Typer(help="AWS commands", no_args_is_help=True)

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
    account_id: str = typer.Option(..., "--account-id", "-a", help="The account ID for the AWS account"),
    role: str = typer.Option(..., "--role", "-r", help="The IAM role Cortex would be assuming"),
):
    """
    Add a single configuration
    """

    client = ctx.obj["client"]

    data = {
       "accountId": account_id,
       "role": role
    }       
    
    r = client.post("api/v1/aws/configurations", data=data)
    print_json(data=r)

@app.command()
def delete(
    ctx: typer.Context,
    account_id: str = typer.Option(..., "--account-id", "-a", help="The account ID for the AWS account"),
):
    """
    Delete a configuration
    """

    client = ctx.obj["client"]

    r = client.delete("api/v1/aws/configurations/" + accountId)
    print_json(data=r)

@app.command()
def delete_all(
    ctx: typer.Context,
):
    """
    Delete a configuration
    """

    client = ctx.obj["client"]

    r = client.delete("api/v1/aws/configurations")
    print_json(data=r)

@app.command()
def get(
    ctx: typer.Context,
    account_id: str = typer.Option(..., "--account-id", "-a", help="The account ID for the AWS account"),
):
    """
    Get a configuration
    """

    client = ctx.obj["client"]

    r = client.get("api/v1/aws/configurations/" + accountId)
    print_json(data=r)

@app.command("list")
def aws_list(
    ctx: typer.Context,
):
    """
    Get all configurations
    """

    client = ctx.obj["client"]

    r = client.get("api/v1/aws/configurations")
    print_json(data=r)


@app.command()
def update(
    ctx: typer.Context,
    configurations: list[str] | None  = typer.Option(None, "--configurations", "-c", callback=_parse_key_value, help="List of account=role pairs (only if file input not provided."),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON file containing configurations; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Update configurations
    """

    client = ctx.obj["client"]

    data = {
       "configurations": []
    }
    series_data = {
       "configurations": configurations
    }

    if file_input:
        data = json.loads("".join([line for line in file_input]))

    if configurations:
        for item in configurations:
           data["configurations"].append(item)

    r = client.put("api/v1/aws/configurations", data=data)
    print_json(data=r)

@app.command()
def validate(
    ctx: typer.Context,
    account_id: str = typer.Option(..., "--account-id", "-a", help="The account ID for the AWS account"),
):
    """
    Validate a configuration
    """

    client = ctx.obj["client"]

    r = client.post("api/v1/aws/configurations/validate" + accountId)
    print_json(data=r)

@app.command()
def validate_all(
    ctx: typer.Context,
):
    """
    Validate all configurations
    """

    client = ctx.obj["client"]

    r = client.post("api/v1/aws/configurations")
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

    r = client.get("api/v1/aws/types", params=params)
    print_json(data=r)

@app.command()
def update_types(
    ctx: typer.Context,
    types: list[str] | None  = typer.Option(None, "--types", "-t", callback=_parse_key_value_types, help="List of type=True|False pairs (only if file input not provided."),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON File containing AWS types that should be discovered and imported into catalog; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Update configured AWS types
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
    r = client.put("api/v1/aws/types", data=data)
    print_json(data=r)
