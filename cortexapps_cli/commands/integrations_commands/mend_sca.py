import json
from rich import print_json
import typer
from typing_extensions import Annotated

app = typer.Typer(help="Mend SCA commands", no_args_is_help=True)

@app.command()
def add(
    ctx: typer.Context,
    org_key: str = typer.Option(None, "--org-key", "-ok", help="Organization key"),
    user_key: str = typer.Option(None, "--user-key", "-uk", help="User key"),
    org_type: str = typer.Option(None, "--org-type", "-ot", help="Organization type"),
    url_type: str = typer.Option(None, "--url-type", "-ut", help="URL type"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON file containing configuration, if command line options not used; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Add a configuration
    """
    client = ctx.obj["client"]

    if file_input:
        if org_key or user_key or org_type or url_type:
            raise typer.BadParameter("When providing a configuration file, do not specify any other attributes")
        data = json.loads("".join([line for line in file_input]))
    else:
        data = {
           "orgKey": org_key,
           "userKey": user_key,
           "orgType": org_type,
           "urlType": url_type,
        }
        data = {k: v for k, v in data.items() if v is not None}

    r = client.post("api/v1/mend/sca/configuration", data=data)
    print_json(data=r)

@app.command()
def get(ctx: typer.Context):
    """
    Get the configuration
    """
    client = ctx.obj["client"]
    r = client.get("api/v1/mend/sca/default-configuration")
    print_json(data=r)

@app.command()
def update(
    ctx: typer.Context,
    org_key: str = typer.Option(None, "--org-key", "-ok", help="Organization key"),
    user_key: str = typer.Option(None, "--user-key", "-uk", help="User key"),
    org_type: str = typer.Option(None, "--org-type", "-ot", help="Organization type"),
    url_type: str = typer.Option(None, "--url-type", "-ut", help="URL type"),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON file containing configuration, if command line options not used; can be passed as stdin with -, example: -f-")] = None,
):
    """
    Update the configuration
    """
    client = ctx.obj["client"]

    if file_input:
        if org_key or user_key or org_type or url_type:
            raise typer.BadParameter("When providing a configuration file, do not specify any other attributes")
        data = json.loads("".join([line for line in file_input]))
    else:
        data = {
           "orgKey": org_key,
           "userKey": user_key,
           "orgType": org_type,
           "urlType": url_type,
        }
        data = {k: v for k, v in data.items() if v is not None}

    r = client.put("api/v1/mend/sca/configuration", data=data)
    print_json(data=r)

@app.command()
def validate(ctx: typer.Context):
    """
    Validate the configuration
    """
    client = ctx.obj["client"]
    r = client.post("api/v1/mend/sca/configuration/validate")
    print_json(data=r)

@app.command()
def delete(ctx: typer.Context):
    """
    Delete the configuration
    """
    client = ctx.obj["client"]
    r = client.delete("api/v1/mend/sca/configurations")
    print_json(data=r)
