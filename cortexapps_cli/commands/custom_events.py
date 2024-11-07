from collections import defaultdict
from datetime import datetime
import json
from rich import print_json
import typer
from typing_extensions import Annotated

app = typer.Typer(help="Custom events commands")

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
def update_by_uuid(
    ctx: typer.Context,
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help=" File containing custom event; can be passed as stdin with -, example: -f-")] = None,
    custom_data: list[str] | None  = typer.Option(None, "--custom", "-c", callback=_parse_key_value, help="List of optional custom metadata key=value pairs (only if file input not provided."),
    description: str = typer.Option(None, "--description", "-d", help="The description of the custom data key (only if file input not provided)."),
    title: str = typer.Option(None, "--title", "-ti",  help="The title of the custome event (only if file input not provided)."),
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    uuid: str = typer.Option(..., "--uuid", "-u", help="UUID of custom event."),
    event: str = typer.Option(None, "--type", "-y", help="The type of the custom event (only required if file input not provided)."),
    url: str = typer.Option(None, "--url", help="The url of the custom event (optional, only required if file input not provided)."),
    timestamp: datetime = typer.Option(datetime.now(), "--timestamp", "-ts", help="Timestamp of custom event, defaults to current time (only if file input not provided)", formats=["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"]),
):
    """
    Create custom event for entity
    """

    client = ctx.obj["client"]

    if file_input:
        if description or title or custom_data or event or url:
            raise typer.BadParameter("When providing a custom event definition file, do not specify any other custom event attributes")
        data = json.loads("".join([line for line in file_input]))
        if timestamp:
            data["timestamp"] = timestamp

    else:
        data = {
            "title": title,
            "timestamp": timestamp,
            "type": event,
            "url": url,
        }

        if description:
            data["description"] = description
        if url:
            data["url"] = url
        if custom_data:
            data["customData"] = dict(custom_data)

    # convert datetime type to string
    for k, v in data.items():
        if str(type(v)) == "<class 'datetime.datetime'>":
           data[k] = v.strftime('%Y-%m-%dT%H:%M:%S')

    r = client.put("api/v1/catalog/" + tag + "/custom-events/" + uuid, data=data)
    print_json(data=r)

@app.command()
def create(
    ctx: typer.Context,
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help=" File containing custom event; can be passed as stdin with -, example: -f-")] = None,
    custom_data: list[str] | None  = typer.Option(None, "--custom", "-c", callback=_parse_key_value, help="List of optional custom metadata key=value pairs (only if file input not provided."),
    description: str = typer.Option(None, "--description", "-d", help="The description of the custom data key (only if file input not provided)."),
    title: str = typer.Option(None, "--title", "-ti",  help="The title of the custome event (only if file input not provided)."),
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    event: str = typer.Option(None, "--type", "-y", help="The type of the custom event (only required if file input not provided)."),
    url: str = typer.Option(None, "--url", "-u", help="The url of the custom event (optional, only required if file input not provided)."),
    timestamp: datetime = typer.Option(datetime.now(), "--timestamp", "-ts", help="Timestamp of custom event, defaults to current time (only if file input not provided)", formats=["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"]),
):
    """
    Create custom event for entity
    """

    client = ctx.obj["client"]

    if file_input:
        if description or title or custom_data or event or url:
            raise typer.BadParameter("When providing a custom event definition file, do not specify any other custom event attributes")
        data = json.loads("".join([line for line in file_input]))
        if timestamp:
            data["timestamp"] = timestamp

    else:
        if not title:
            raise typer.BadParameter("title is required if custom event file is not provided")
        if not event:
            raise typer.BadParameter("type is required if custom event file is not provided")

        data = {
            "title": title,
            "timestamp": timestamp,
            "type": event,
            "url": url,
        }

        if description:
            data["description"] = description
        if url:
            data["url"] = url
        if custom_data:
            data["customData"] = dict(custom_data)

    # convert datetime type to string
    for k, v in data.items():
        if str(type(v)) == "<class 'datetime.datetime'>":
           data[k] = v.strftime('%Y-%m-%dT%H:%M:%S')

    r = client.post("api/v1/catalog/" + tag + "/custom-events", data=data)
    print_json(data=r)

@app.command()
def delete_all(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    event: str = typer.Option(None, "--type", "-y", help="The type of the custom event, defaults to all."),
    timestamp: datetime = typer.Option(None, "--timestamp", "-ts", help="Optional timestamp of custom events to delete.", formats=["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"]),
):
    """
    Delete all custom events for an entity
    """

    client = ctx.obj["client"]

    params = {
        "type": event,
        "timestamp": timestamp
    }

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    # convert datetime type to string
    for k, v in params.items():
        if str(type(v)) == "<class 'datetime.datetime'>":
           params[k] = v.strftime('%Y-%m-%dT%H:%M:%S')

    r = client.delete("api/v1/catalog/" + tag + "/custom-events", params=params)

@app.command()
def list(
    ctx: typer.Context,
    page: int | None = typer.Option(None, "--page", "-p", help="Page number to return, 0 indexed - omit to fetch all pages"),
    page_size: int | None = typer.Option(None, "--page-size", "-z", help="Page size for results"),
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    event: str = typer.Option(None, "--type", "-y", help="The type of the custom event, defaults to all."),
    timestamp: datetime = typer.Option(None, "--timestamp", "-ts", help="Optional timestamp of custom events to delete.", formats=["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"]),
):
    """
    List custom events for entity
    """
    client = ctx.obj["client"]

    params = {
        "page": page,
        "pageSize": page_size,
        "timestamp": timestamp,
        "type": event
    }

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    # convert datetime type to string
    for k, v in params.items():
        if str(type(v)) == "<class 'datetime.datetime'>":
           params[k] = v.strftime('%Y-%m-%dT%H:%M:%S')

    client.fetch_or_get("api/v1/catalog/" + tag + "/custom-events", page, params=params)

@app.command()
def get_by_uuid(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    uuid: str = typer.Option(..., "--uuid", "-u", help="UUID of custom event."),
):
    """
    Get custom event by UUID
    """
    client = ctx.obj["client"]

    r = client.get("api/v1/catalog/" + tag + "/custom-events/" + uuid)
    print_json(data=r)

@app.command()
def delete_by_uuid(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    uuid: str = typer.Option(..., "--uuid", "-u", help="UUID of custom event."),
):
    """
    Delete custom events by UUID
    """
    client = ctx.obj["client"]

    r = client.delete("api/v1/catalog/" + tag + "/custom-events/" + uuid)