from collections import defaultdict
import json
from rich import print_json
import typer
from typing_extensions import Annotated

app = typer.Typer(help="Dependency commands", no_args_is_help=True)

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
def create(
    ctx: typer.Context,
    callee_tag: str = typer.Option(..., "--callee-tag", "-e", help="The entity tag (x-cortex-tag) for the caller entity (\"to\" entity)"),
    caller_tag: str = typer.Option(..., "--caller-tag", "-r", help="The entity tag (x-cortex-tag) for the caller entity (\"from\" entity)"),
    description: str = typer.Option("", "--description", "-d", help="The description of the dependency"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help=" File containing dependency metadata; can be passed as stdin with -, example: -f-")] = None,
    metadata: list[str] | None  = typer.Option(None, "--custom", "-c", callback=_parse_key_value, help="List of optional metadata key=value pairs (only; will be merged with file input"),
    method: str = typer.Option(None, "--method", "-m",  help="The HTTP method type of the dependency"),
    path: str = typer.Option(None, "--path", "-p", help="The path of the dependency")
):
    """
    Create dependency from entity
    """

    client = ctx.obj["client"]

    if file_input:
        if description or metadata or method or path or caller_tag or callee_tag:
            raise typer.BadParameter("When providing a dependencies input file, do not specify any other dependency event attributes")
        data = json.loads("".join([line for line in file_input]))
    else:
        params = {
        }

        if method:
            params["method"] = method
        if path:
            params["path"] = path

        data = {
          "description": "",
          "metadata": {
          }
        }

    if metadata:
        data["metadata"] = dict(metadata)

    if description:
        data["description"] = description

    r = client.post("api/v1/catalog/" + caller_tag + "/dependencies/" + callee_tag, data=data, params=params)
    print_json(json.dumps(r))

@app.command()
def delete_in_bulk(
    ctx: typer.Context,
    file_input: Annotated[typer.FileText, typer.Option(..., "--file", "-f", help=" File containing dependency values to delete; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Delete dependencies in bulk, see https://docs.cortex.io/docs/api/delete-dependencies-in-bulk for format of input file
    """

    client = ctx.obj["client"]

    data = json.loads("".join([line for line in file_input]))

    r = client.delete("api/v1/catalog/dependencies", data=data)

@app.command()
def add_in_bulk(
    ctx: typer.Context,
    file_input: Annotated[typer.FileText, typer.Option(..., "--file", "-f", help=" File containing dependency values to create or update; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Create or update dependencies in bulk, see https://docs.cortex.io/docs/api/create-or-update-dependencies-in-bulk
    """

    client = ctx.obj["client"]

    data = json.loads("".join([line for line in file_input]))

    r = client.put("api/v1/catalog/dependencies", data=data)

@app.command()
def delete_all(
    ctx: typer.Context,
    caller_tag: str = typer.Option(..., "--caller-tag", "-r", help="The entity tag (x-cortex-tag) for the caller entity (\"from\" entity)"),
):
    """
    Deletes any outgoing dependencies that were created via the API from the entity
    """

    client = ctx.obj["client"]

    r = client.delete("api/v1/catalog/" + caller_tag + "/dependencies")

@app.command()
def get_all(
    ctx: typer.Context,
    caller_tag: str = typer.Option(..., "--caller-tag", "-r", help="The entity tag (x-cortex-tag) for the caller entity (\"from\" entity)"),
    include_incoming: bool = typer.Option(True, "--include-incoming", "-i", help="Include incoming dependencies"),
    include_outgoing: bool = typer.Option(False, "--include-outgoing", "-o", help="Include outgoing dependencies"),
    page: int = typer.Option(None, "--page", "-p", help="Page number to return, 0 indexed - omit to fetch all pages"),
    page_size: int = typer.Option(None, "--page-size", "-z", help="Page size for results"),
    prt: bool = typer.Option(True, "--print", help="If result should be printed to the terminal", hidden=True),
):
    """
    Retrieve all dependencies for an entity
    """

    params = {
        "includeIncoming": include_incoming,
        "includeOutgoing": include_outgoing,
        "page": page,
        "pageSize": page_size
    }

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    client = ctx.obj["client"]

    client.fetch_or_get("api/v1/catalog/" + caller_tag + "/dependencies", page, prt, params=params)

@app.command()
def delete(
    ctx: typer.Context,
    callee_tag: str = typer.Option(..., "--callee-tag", "-e", help="The entity tag (x-cortex-tag) for the caller entity (\"to\" entity)"),
    caller_tag: str = typer.Option(..., "--caller-tag", "-r", help="The entity tag (x-cortex-tag) for the caller entity (\"from\" entity)"),
    method: str = typer.Option(None, "--method", "-m",  help="The HTTP method type of the dependency"),
    path: str = typer.Option(None, "--path", "-p", help="The path of the dependency")
):
    """
    Delete a dependency from an entity
    """

    params = {
        "method": method,
        "path": path
    }

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    client = ctx.obj["client"]

    r = client.delete("api/v1/catalog/" + caller_tag + "/dependencies/" + callee_tag, params=params)

@app.command()
def get(
    ctx: typer.Context,
    callee_tag: str = typer.Option(..., "--callee-tag", "-e", help="The entity tag (x-cortex-tag) for the caller entity (\"to\" entity)"),
    caller_tag: str = typer.Option(..., "--caller-tag", "-r", help="The entity tag (x-cortex-tag) for the caller entity (\"from\" entity)"),
    method: str = typer.Option(None, "--method", "-m",  help="The HTTP method type of the dependency"),
    path: str = typer.Option(None, "--path", "-p", help="The path of the dependency")
):
    """
    Retrieve dependency between entities
    """

    params = {
        "method": method,
        "path": path
    }

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    client = ctx.obj["client"]

    r = client.get("api/v1/catalog/" + caller_tag + "/dependencies/" + callee_tag, params=params)

    print_json(data=r)

@app.command()
def update(
    ctx: typer.Context,
    callee_tag: str = typer.Option(..., "--callee-tag", "-e", help="The entity tag (x-cortex-tag) for the caller entity (\"to\" entity)"),
    caller_tag: str = typer.Option(..., "--caller-tag", "-r", help="The entity tag (x-cortex-tag) for the caller entity (\"from\" entity)"),
    description: str = typer.Option("", "--description", "-d", help="The description of the dependency"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help=" File containing dependency metadata; can be passed as stdin with -, example: -f-")] = None,
    metadata: list[str] | None  = typer.Option(None, "--custom", "-c", callback=_parse_key_value, help="List of optional metadata key=value pairs; will be merged with file input"),
    method: str = typer.Option(None, "--method", "-m",  help="The HTTP method type of the dependency"),
    path: str = typer.Option(None, "--path", "-p", help="The path of the dependency")
):
    """
    Update dependency between entities
    """

    client = ctx.obj["client"]

    params = {
    }

    if method:
        params["method"] = method
    if path:
        params["path"] = path

    data = {
      "description": "",
      "metadata": {
      }
    }

    if file_input:
        data = json.loads("".join([line for line in file_input]))

    # if metadata provided in file and command line, command line takes precedence
    if metadata:
        data["metadata"] = data["metadata"] | dict(metadata)

    if description:
        data["description"] = description

    r = client.put("api/v1/catalog/" + caller_tag + "/dependencies/" + callee_tag, data=data, params=params)
    print_json(data=r)
