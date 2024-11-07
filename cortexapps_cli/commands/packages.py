import json
from rich import print_json
import typer
import cortexapps_cli.commands.packages_commands.go as go
import cortexapps_cli.commands.packages_commands.java as java
import cortexapps_cli.commands.packages_commands.python as python
import cortexapps_cli.commands.packages_commands.node as node
import cortexapps_cli.commands.packages_commands.nuget as nuget

app = typer.Typer(help="Packages commands")
app.add_typer(go.app, name="go")
app.add_typer(java.app, name="java")
app.add_typer(python.app, name="python")
app.add_typer(node.app, name="node")
app.add_typer(nuget.app, name="nuget")

@app.command()
def list(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    page: int | None = typer.Option(None, "--page", "-p", help="Page number to return, 0 indexed - omit to fetch all pages"),
    page_size: int | None = typer.Option(None, "--page-size", "-z", help="Page size for results"),
):
    """
    List packages for entity
    """

    client = ctx.obj["client"]

    params = {
       "page": page,
       "pageSize": page_size
    }       

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}
    
    client.fetch_or_get("api/v1/catalog/" + tag_or_id + "/packages", page, params=params)

@app.command()
def delete_all(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
):
    """
    Delete all packages for entity
    """

    client = ctx.obj["client"]

    response = client.get("api/v1/catalog/" + tag_or_id + "/packages")
    for package in response:
        name = package['name']
        package_type = package['packageType']
        if package_type == "NUGET":
            package_path = "dotnet/nuget"
        else:
            package_path = package_type.lower()
        client.delete("api/v1/catalog/" + tag_or_id + "/packages/" + package_path, params={"name": name})
