import json
from rich import print_json
import typer
import cortexapps_cli.commands.packages_commands.go as go
import cortexapps_cli.commands.packages_commands.java as java
import cortexapps_cli.commands.packages_commands.python as python
import cortexapps_cli.commands.packages_commands.node as node
import cortexapps_cli.commands.packages_commands.nuget as nuget
from cortexapps_cli.command_options import ListCommandOptions
from cortexapps_cli.utils import print_output_with_context, print_output

app = typer.Typer(
    help="Packages commands",
    no_args_is_help=True
)

app.add_typer(go.app, name="go")
app.add_typer(java.app, name="java")
app.add_typer(python.app, name="python")
app.add_typer(node.app, name="node")
app.add_typer(nuget.app, name="nuget")

@app.command()
def list(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    table_output: ListCommandOptions.table_output = False,
    csv_output: ListCommandOptions.csv_output = False,
    columns: ListCommandOptions.columns = [],
    no_headers: ListCommandOptions.no_headers = False,
    filters: ListCommandOptions.filters = [],
    sort: ListCommandOptions.sort = [],
):
    """
    List packages for entity
    """

    client = ctx.obj["client"]

    if (table_output or csv_output) and not ctx.params.get('columns'):
        ctx.params['columns'] = [
            "Id=id",
            "PackageType=packageType",
            "Name=name",
            "Version=version",
            "DateCreated=dateCreated",
        ]

    # NOTE: packages list is not paginated, so no if-else that includes client.fetch.
    r = client.get("api/v1/catalog/" + tag_or_id + "/packages")
    print_output_with_context(ctx, r)

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
