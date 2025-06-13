import typer
from typing_extensions import Annotated

app = typer.Typer(help="Node commands")

@app.command()
def upload_package_json(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    package_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File containing contents of package.json; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Upload node package.json file
    """

    client = ctx.obj["client"]
    
    client.post("api/v1/catalog/" + tag_or_id + "/packages/node/package-json", data=package_input.read())

@app.command()
def upload_package_lock(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    package_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File containing contents of package.lock; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Upload node package-lock.json file
    """

    client = ctx.obj["client"]
    
    client.post("api/v1/catalog/" + tag_or_id + "/packages/node/package-lock", data=package_input.read())

@app.command()
def upload_yarn_lock(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    package_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File containing contents of yarn.lock; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Upload node yarn.lock file
    """

    client = ctx.obj["client"]
    
    client.post("api/v1/catalog/" + tag_or_id + "/packages/node/yarn-lock", data=package_input.read())
    

@app.command()
def delete(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    name: str = typer.Option(..., "--name", "-n", help="The name of the package to delete"),
):
    """
    Delete node package from entity
    """

    client = ctx.obj["client"]

    params = {
       "name": name
    }       
    
    client.delete("api/v1/catalog/" + tag_or_id + "/packages/node", params=params)
