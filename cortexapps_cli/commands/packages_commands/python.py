import typer
from typing_extensions import Annotated

app = typer.Typer(help="Python commands")

@app.command()
def upload_pipfile(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    package_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File containing contents of pipfile.lock; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Upload python pipfile.lock file
    """

    client = ctx.obj["client"]
    
    client.post("api/v1/catalog/" + tag_or_id + "/packages/python/pipfile", data=package_input.read(), content_type='application/text')

@app.command()
def upload_requirements(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    package_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File containing contents of requirements.txt; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Upload python requirements.txt file
    """

    client = ctx.obj["client"]
    
    client.post("api/v1/catalog/" + tag_or_id + "/packages/python/requirements", data=package_input.read(), content_type='application/text')
    

@app.command()
def delete(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    name: str = typer.Option(..., "--name", "-n", help="The name of the package to delete"),
):
    """
    Delete python package from entity
    """

    client = ctx.obj["client"]

    params = {
       "name": name
    }       
    
    client.delete("api/v1/catalog/" + tag_or_id + "/packages/python", params=params)
