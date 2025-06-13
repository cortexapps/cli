import json
from rich import print_json
import typer
from typing_extensions import Annotated
import yaml

app = typer.Typer(help="Docs commands", no_args_is_help=True)

@app.command()
def get(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    name: str = typer.Option(None, "--name", "-n", help="Name of the OpenAPI spec to return. If you have multiple OpenAPI specs configured for your entity as x-cortex-links, use this parameter to ensure the correct spec is returned. If this parameter is not specified, we will return the first OpenAPI spec found."),
):
    """
    Get OpenAPI docs for entity
    """

    client = ctx.obj["client"]

    params = {
       "name": name
    }       

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    r = client.get("api/v1/catalog/" + tag + "/documentation/openapi", params=params)

    print_json(data=r)

@app.command()
def update(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help=" File containing stringified JSON representation of the OpenAPI spec; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Update OpenAPI docs for entity
    """

    client = ctx.obj["client"]

    yaml_content = yaml.safe_load("".join([line for line in file_input]))

    data = json.dumps({"spec": "" + str(yaml_content) + ""})

    r = client.put("api/v1/catalog/" + tag + "/documentation/openapi", data=data)

    print_json(data=r)

@app.command()
def delete(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
):
    """
    Delete OpenAPI docs for entity
    """

    client = ctx.obj["client"]

    r = client.delete("api/v1/catalog/" + tag + "/documentation/openapi")
