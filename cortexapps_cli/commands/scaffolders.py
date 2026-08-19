from cortexapps_cli.command_options import CommandOptions
from cortexapps_cli.command_options import ListCommandOptions
from cortexapps_cli.utils import print_output_with_context, print_output
from typing_extensions import Annotated
import json
import typer
import yaml

app = typer.Typer(
    help="Scaffolder template commands",
    no_args_is_help=True
)

def _is_valid_yaml(filepath):
    try:
        yaml.safe_load(filepath)
        filepath.seek(0)
        return True
    except yaml.YAMLError:
        return False

def _is_valid_json(filepath):
    try:
        json.load(filepath)
        filepath.seek(0)
        return True
    except json.JSONDecodeError:
        return False

def _read_definition(file_input):
    if _is_valid_json(file_input):
        content_type = "application/json"
        data = json.loads("".join([line for line in file_input]))
    elif _is_valid_yaml(file_input):
        data = file_input.read()
        content_type = "application/yaml"
    else:
        raise typer.BadParameter("Input file is neither valid JSON nor YAML.")
    return data, content_type

@app.command()
def list(
    ctx: typer.Context,
    _print: CommandOptions._print = True,
    page: ListCommandOptions.page = None,
    page_size: ListCommandOptions.page_size = 250,
    table_output: ListCommandOptions.table_output = False,
    csv_output: ListCommandOptions.csv_output = False,
    columns: ListCommandOptions.columns = [],
    no_headers: ListCommandOptions.no_headers = False,
    filters: ListCommandOptions.filters = [],
    sort: ListCommandOptions.sort = [],
):
    """
    List Scaffolder templates.
    """

    client = ctx.obj["client"]

    params = {
       "page": page,
       "pageSize": page_size
    }

    if (table_output or csv_output) and not ctx.params.get('columns'):
        ctx.params['columns'] = [
            "Tag=tag",
            "Name=name",
            "Description=description",
        ]

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    if page is None:
        # if page is not specified, we want to fetch all pages
        r = client.fetch("api/v1/scaffolders", params=params)
    else:
        # if page is specified, we want to fetch only that page
        r = client.get("api/v1/scaffolders", params=params)

    if _print:
        print_output_with_context(ctx, r)
    else:
        return(r)

@app.command()
def get(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag or unique, auto-generated Cortex ID of the Scaffolder template"),
    yaml: bool = typer.Option(False, "--yaml", "-y", help="When true, returns the YAML representation of the template."),
    _print: CommandOptions._print = True,
):
    """
    Retrieve Scaffolder template by tag or Cortex ID.
    """

    client = ctx.obj["client"]

    if yaml:
        headers={'Accept': 'application/yaml'}
    else:
        headers={'Accept': 'application/json'}
    r = client.get("api/v1/scaffolders/" + tag, headers=headers)

    if _print:
        if yaml:
           print(r)
        else:
           print_output_with_context(ctx, r)
    else:
        return(r)

@app.command()
def create(
    ctx: typer.Context,
    file_input: Annotated[typer.FileText, typer.Option(..., "--file", "-f", help="File containing the Scaffolder template definition; can be passed as stdin with -, example: -f-")],
):
    """
    Create or update a Scaffolder template.  API key must have the Configure Scaffolder permission.  Note: If a Scaffolder template with the same tag already exists, it will be updated.
    """

    client = ctx.obj["client"]

    data, content_type = _read_definition(file_input)
    r = client.post("api/v1/scaffolders", data=data, content_type=content_type)
    print_output(r)

@app.command()
def update(
    ctx: typer.Context,
    tag: Annotated[str, typer.Option(..., "--tag", "-t", help="The tag or unique, auto-generated Cortex ID of the Scaffolder template")],
    file_input: Annotated[typer.FileText, typer.Option(..., "--file", "-f", help="File containing the Scaffolder template definition; can be passed as stdin with -, example: -f-")],
):
    """
    Update a Scaffolder template by tag or Cortex ID.  API key must have the Configure Scaffolder permission.
    """

    client = ctx.obj["client"]

    data, content_type = _read_definition(file_input)
    r = client.put("api/v1/scaffolders/" + tag, data=data, content_type=content_type)
    print_output(r)

@app.command()
def delete(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag or unique, auto-generated Cortex ID of the Scaffolder template"),
):
    """
    Delete Scaffolder template by tag or Cortex ID.  API key must have the Configure Scaffolder permission.
    """

    client = ctx.obj["client"]

    r = client.delete("api/v1/scaffolders/" + tag)
