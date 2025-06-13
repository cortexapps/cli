import typer
from typing_extensions import Annotated

app = typer.Typer(help="Go commands")

@app.command()
def upload(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    package_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File containing contents of go.sum; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Upload go.sum package
    """

    client = ctx.obj["client"]
    
    #client.post("api/v1/catalog/" + tag_or_id + "/packages/go/gosum", data=package_input.read(), content_type='application/text')
    client.post("api/v1/catalog/" + tag_or_id + "/packages/go/gosum", data=package_input.read())
    
@app.command()
def delete(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    name: str = typer.Option(..., "--name", "-n", help="The name of the package to delete"),
):
    """
    Delete go package from entity
    """

    client = ctx.obj["client"]

    params = {
       "name": name
    }       
    
    client.delete("api/v1/catalog/" + tag_or_id + "/packages/go", params=params)
