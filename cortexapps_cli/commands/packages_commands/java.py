import typer
from typing_extensions import Annotated

app = typer.Typer(help="Java commands")

@app.command()
def upload_single(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    package_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File containing package name and version; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Upload single Java package
    """

    client = ctx.obj["client"]
    
    client.post("api/v1/catalog/" + tag_or_id + "/packages/java", data=package_input.read())

@app.command()
def upload_multiple(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    package_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File containing multiple package names and versions; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Upload multiple Java packages
    """

    client = ctx.obj["client"]
    
    client.post("api/v1/catalog/" + tag_or_id + "/packages/java/bulk", data=package_input.read())
    

@app.command()
def delete(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    name: str = typer.Option(..., "--name", "-n", help="The name of the package to delete"),
):
    """
    Delete Java package from entity
    """

    client = ctx.obj["client"]

    params = {
       "name": name
    }       
    
    client.delete("api/v1/catalog/" + tag_or_id + "/packages/java", params=params)
