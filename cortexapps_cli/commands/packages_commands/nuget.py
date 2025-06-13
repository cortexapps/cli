import typer
from typing_extensions import Annotated

app = typer.Typer(help="NuGet commands")

@app.command()
def upload_csproj(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    package_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File containing contents of NuGet csproj file; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Upload NuGet csproj file
    """

    client = ctx.obj["client"]
    
    client.post("api/v1/catalog/" + tag_or_id + "/packages/dotnet/nuget/csproj", data=package_input.read())

@app.command()
def upload_packages_lock(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    package_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File containing contents of NuGet packages.lock; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Upload NuGet packages.lock file
    """

    client = ctx.obj["client"]
    
    client.post("api/v1/catalog/" + tag_or_id + "/packages/dotnet/nuget/packages-lock", data=package_input.read())
    
@app.command()
def delete(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    name: str = typer.Option(..., "--name", "-n", help="The name of the package to delete"),
):
    """
    Delete NuGet package from entity
    """

    client = ctx.obj["client"]

    params = {
       "name": name
    }       
    
    client.delete("api/v1/catalog/" + tag_or_id + "/packages/dotnet/nuget", params=params)
