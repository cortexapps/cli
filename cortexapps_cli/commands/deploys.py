from collections import defaultdict
from datetime import datetime
from enum import Enum
import json
from rich import print_json
import typer
from typing_extensions import Annotated

app = typer.Typer(help="Deploys commands", no_args_is_help=True)

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

class Type(str, Enum):
    DEPLOY = "DEPLOY"
    SCALE = "SCALE"
    ROLLBACK = "ROLLBACK"
    RESTART = "RESTART"

@app.command()
def delete_by_filter(
    ctx: typer.Context,
    sha: str = typer.Option(None, "--sha", "-s", help="The Secure Hash Algorithm (SHA) of the deploy"),
    environment: str = typer.Option(None, "--environment", "-e", help="The name of the environment"),
    type: Type = typer.Option(None, "--type", "-ty", help="The type of the deploy"),
):
    """
    Filter and delete deploys by SHA hash, environment or type
    """

    client = ctx.obj["client"]

    if not sha and not environment and not type:
        raise typer.BadParameter("At least one of sha, environment or type must be provided.")

    params = {
       "environment": environment,
       "sha": sha,
       "type": type
    }       

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}
    
    client.delete("api/v1/catalog/deploys", params=params)

@app.command()
def delete_all(
    ctx: typer.Context,
):
    """
    Dangerous endpoint that blows away deploys for all entities
    """

    client = ctx.obj["client"]

    client.delete("api/v1/catalog/deploys/all")

@app.command()
def delete(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity"),
    sha: str = typer.Option(None, "--sha", "-s", help="The Secure Hash Algorithm (SHA) of the deploy"),
    environment: str = typer.Option(None, "--environment", "-e", help="The name of the environment"),
    type: Type = typer.Option(None, "--type", "-ty", help="The type of the deploy"),
):
    """
    Delete deployments for entity
    """

    client = ctx.obj["client"]

    params = {
       "environment": environment,
       "sha": sha,
       "type": type
    }       

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    client.delete("api/v1/catalog/" + tag + "/deploys", params=params)

# 'list' is a keyword in python; naming the function 'list' will cause problems like this:
# TypeError: 'function' object is not subscriptable
#
# Because of this subsequent line in the file:
# customData: list[str] | None  = typer.Option(None, "--custom", "-c", callback=_parse_key_value, help="List of optional custom metadata key=value pairs"),
# 
# There is a collision between naming this function 'list' and then expecting to use list as the python built-in.
@app.command("list")
def deploys_list(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity"),
    page: int | None = typer.Option(None, "--page", "-p", help="Page number to return, 0 indexed - omit to fetch all pages"),
    page_size: int | None = typer.Option(None, "--page-size", "-z", help="Page size for results"),
    prt: bool = typer.Option(True, "--print", help="If result should be printed to the terminal", hidden=True),
):
    """
    List deployments for entity
    """

    client = ctx.obj["client"]
    
    params = {
       "page": page,
       "pageSize": page_size
    }       

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    client.fetch_or_get("api/v1/catalog/" + tag + "/deploys", page, prt, params=params)

@app.command()
def add(
    ctx: typer.Context,
    customData: list[str] | None  = typer.Option(None, "--custom", "-c", callback=_parse_key_value, help="List of optional custom metadata key=value pairs"),
    email: str = typer.Option(None, "--email", "-m", help="Email address of deployer"),
    environment: str = typer.Option(None, "--environment", "-e", help="The name of the environment"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help=" File containing dependency metadata; can be passed as stdin with -, example: -f-")] = None,
    name: str = typer.Option(None, "--name", "-n", help="Name of deployer"),
    sha: str = typer.Option(None, "--sha", "-s", help="The Secure Hash Algorithm (SHA) of the deploy"),
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity"),
    timestamp: datetime = typer.Option(datetime.now(), "--timestamp", "-ts", help="Timestamp of the deploy", formats=["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"]),
    title: str = typer.Option(None, "--title", "-ti", help="The title of the deploy"),
    type: Type = typer.Option(None, "--type", "-ty", help="The type of the deploy"),
    url: str = typer.Option(None, "--url", help="The Uniform Resource Locator(URL) of the deploy")
):
    """
    Add deployment for entity
    """

    client = ctx.obj["client"]

    if file_input:
        if email or environment or name or sha or title or type or url:
            raise typer.BadParameter("When providing a deploy input file, do not specify any other deploy event attributes")
        data = json.loads("".join([line for line in file_input]))
    else:

        data = {
          "customData": {
          },
          "deployer": {
             "email": email,
             "name": name
          },
          "environment": environment,
          "sha": sha,
          "timestamp": timestamp,
          "title": title,
          "type": type.value,
          "url": url
        }

        if customData:
            data["customData"] = dict(customData)
        data["timestamp"] = data["timestamp"].strftime('%Y-%m-%dT%H:%M:%SZ')

    r = client.post("api/v1/catalog/" + tag + "/deploys", data=data)
    print_json(data=r)

@app.command()
def delete_by_uuid(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity"),
    uuid: str = typer.Option(..., "--uuid", "-u", help="The Universally Unique Identifier (UUID) of the deploy")
):
    """
    Delete deployment by uuid
    """

    client = ctx.obj["client"]
    
    client.delete("api/v1/catalog/" + tag + "/deploys/" + uuid)

@app.command()
def update_by_uuid(
    ctx: typer.Context,
    customData: list[str] | None  = typer.Option(None, "--custom", "-c", callback=_parse_key_value, help="List of optional custom metadata key=value pairs"),
    email: str = typer.Option(None, "--email", "-m", help="Email address of deployer"),
    environment: str = typer.Option(None, "--environment", "-e", help="The name of the environment"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help=" File containing dependency metadata; can be passed as stdin with -, example: -f-")] = None,
    name: str = typer.Option(None, "--name", "-n", help="Name of deployer"),
    sha: str = typer.Option(None, "--sha", "-s", help="The Secure Hash Algorithm (SHA) of the deploy"),
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity"),
    timestamp: datetime = typer.Option(datetime.now(), "--timestamp", "-ts", help="Timestamp of the deploy", formats=["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"]),
    title: str = typer.Option(None, "--title", "-ti", help="The title of the deploy"),
    deploy_type: Type = typer.Option(None, "--type", "-ty", help="The type of the deploy"),
    url: str = typer.Option(None, "--url", help="The Uniform Resource Locator(URL) of the deploy"),
    uuid: str = typer.Option(..., "--uuid", "-u", help="The Universally Unique Identifier (UUID) of the deploy")
):
    """
    Update deployment for entity
    """

    client = ctx.obj["client"]

    if file_input:
        if customData or email or environment or name or sha or title or deploy_type or url:
            raise typer.BadParameter("When providing a deploy input file, do not specify any other deploy event attributes")
        data = json.loads("".join([line for line in file_input]))
    else:

        if not title or tag or deploy_type:
            raise typer.BadParameter("When not providing a deploy input file, title and tag are required")
        data = {
          "environment": environment,
          "sha": sha,
          "type": deploy_type.value,
          "timestamp": timestamp,
          "title": title
        }

        # remove any data valus that are None
        data = {k: v for k, v in data.items() if v is not None}

        if customData:
            data["customData"] = dict(customData)
        if email or name:
            data["deployer"] = {}
            if email:
                data["deployer"]["email"] = email
            if name:
                data["deployer"]["name"] = name
        data["timestamp"] = data["timestamp"].strftime('%Y-%m-%dT%H:%M:%SZ')

    r = client.put("api/v1/catalog/" + tag + "/deploys/" + uuid, data=data)
    print_json(data=r)
