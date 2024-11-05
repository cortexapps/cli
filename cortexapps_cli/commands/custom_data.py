import json
import typer
from typing_extensions import Annotated

from rich import print_json

app = typer.Typer(help="Custom data commands")
# Need a helper function to parse custom_data.
# cannot do this in type: list[Tuple[str, str]] | None  = typer.Option(None)
# Results in: 
# AssertionError: List types with complex sub-types are not currently supported
#
# borrowed from https://github.com/fastapi/typer/issues/387
def _parse_key_value(values):
    if values is None:
        return ""
    result = {}
    for value in values:
        k, v = value.split('=')
        result[k] = v
    return result.items()

@app.command()
def add(
    ctx: typer.Context,
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help=" File containing keys to update; can be passed as stdin with -, example: -f-")] = None,
    force: bool = typer.Option(False, "--force", "-o", help="When true, overrides values that were defined in the catalog descriptor. Will be overwritten the next time the catalog descriptor is processed."),
    key: str = typer.Option(None, "--key", "-k", help="The custom data key to create (only if file input not provided)."),
    value: str = typer.Option(None, "--value", "-v", help="The value of the custom data key (only if file input not provided)."),
    description: str = typer.Option(None, "--description", "-d", help="The description of the custom data key (only if file input not provided)."),
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
):
    """
    Add custom data for entity
    """
    client = ctx.obj["client"]

    params = {
        "force": force,
    }

    if file_input:
        if description or key or value:
            raise typer.BadParameter("When providing a custom input definition file, do not specify any other custom data attributes")
        data = json.loads("".join([line for line in file_input]))
    else:
        if not value:
            raise typer.BadParameter("value is required if custom data file is not provided")
        if not key:
            raise typer.BadParameter("key is required if custom data file is not provided")

        data = {
            "key": key,
            "value": value
        }

        if description:
            data["description"] = description

    r = client.post("api/v1/catalog/" + tag + "/custom-data", data=data, params=params)
    print_json(data=r)

@app.command()
def bulk(
    ctx: typer.Context,
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help=" File containing keys to update; can be passed as stdin with -, example: -f-")] = None,
    force: bool = typer.Option(False, "--force", "-o", help="When true, overrides values that were defined in the catalog descriptor. Will be overwritten the next time the catalog descriptor is processed."),
):
    """
    Add multiple key/values of custom data to multiple entities
    """
    client = ctx.obj["client"]

    data = json.loads("".join([line for line in file_input]))

    params = {
        "force": force
    }

    r = client.put("api/v1/catalog/custom-data", data=data, params=params)
    print_json(data=r)

@app.command()
def delete(
    ctx: typer.Context,
    force: bool = typer.Option(False, "--force", "-o", help="When true, overrides values that were defined in the catalog descriptor. Will be overwritten the next time the catalog descriptor is processed."),
    key: str = typer.Option(..., "--key", "-k", help="The custom metadata key"),
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
):
    """
    Delete custom data for entity
    """
    client = ctx.obj["client"]

    params = {
        "force": force,
        "key": key
    }

    r = client.delete("api/v1/catalog/" + tag + "/custom-data", params=params)

@app.command()
def get(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    key: str = typer.Option(..., "--key", "-k", help="The custom metadata key"),
):
    """
    Retrieve custom data for entity by key
    """
    client = ctx.obj["client"]

    r = client.get("api/v1/catalog/" + tag + "/custom-data/" + key)

    print_json(data=r)

@app.command()
def list(
    ctx: typer.Context,
    page: int | None = typer.Option(None, "--page", "-p", help="Page number to return, 0 indexed - omit to fetch all pages"),
    page_size: int | None = typer.Option(None, "--page-size", "-z", help="Page size for results"),
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
):
    """
    List custom data for entity
    """
    client = ctx.obj["client"]

    params = {
        "page": page,
        "pageSize": page_size
    }

    client.fetch_or_get("api/v1/catalog/" + tag + "/custom-data", page, params=params)
