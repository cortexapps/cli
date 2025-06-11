from cortexapps_cli.command_options import CommandOptions
from cortexapps_cli.command_options import ListCommandOptions
from cortexapps_cli.utils import print_output_with_context, print_output
from typing_extensions import Annotated
import json
import typer
import yaml

app = typer.Typer(
    help="Workflows commands",
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

@app.command()
def list(
    ctx: typer.Context,
    include_actions: bool = typer.Option(False, "--include-actions", "-i", help="When true, returns the list of actions for each workflow. Defaults to false"),
    search_query: str = typer.Option(None, "--search-query", "-s", help="When set, only returns workflows with the given substring in the name or description"),
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
    Get users based on provided criteria.  API key must have the View workflows permission
    """

    client = ctx.obj["client"]

    params = {
       "includeActions": include_actions,
       "searchQuery": search_query,
       "page": page,
       "pageSize": page_size
    }       

    if (table_output or csv_output) and not ctx.params.get('columns'):
        ctx.params['columns'] = [
            "Name=name",
            "Tag=tag",
            "Description=description",
        ]

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}
    
    if page is None:
        # if page is not specified, we want to fetch all pages
        r = client.fetch("api/v1/workflows", params=params)
    else:
        # if page is specified, we want to fetch only that page
        r = client.get("api/v1/workflows", params=params)

    if _print:
        data = r
        print_output_with_context(ctx, data)
    else:
        return(r)

@app.command()
def get(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag or unique, auto-generated identifier for the workflow"),
    yaml: bool = typer.Option(False, "--yaml", "-y", help="When true, returns the YAML representation of the descriptor."),
    _print: CommandOptions._print = True,
):
    """
    Retrieve workflow by tag or ID.  API key must have the View workflows permission.
    """

    client = ctx.obj["client"]

    if yaml:
        headers={'Accept': 'application/yaml'}
    else:
        headers={'Accept': 'application/json'}
    r = client.get("api/v1/workflows/" + tag, headers=headers)

    if _print:
        if yaml:
           print(r)
        else:
           print_output_with_context(ctx, r)
    else:
        if yaml:
           return(r)
        else:
           print_output_with_context(ctx, r)

@app.command()
def delete(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag or unique, auto-generated identifier for the workflow"),
):
    """
    Delete workflow by tag or ID.  API key must have the Edit workflows permission.
    """

    client = ctx.obj["client"]

    r = client.delete("api/v1/workflows/" + tag)

@app.command()
def create(
    ctx: typer.Context,
    file_input: Annotated[typer.FileText, typer.Option(..., "--file", "-f", help=" File containing workflow definition; can be passed as stdin with -, example: -f-")],
):
    """
    Create or update new workflow.  API key must have the Edit workflows permission.  Note: If a workflow with the same tag already exists, it will be updated.
    """

    client = ctx.obj["client"]

    if _is_valid_json(file_input):
        content_type="application/json"
        data = json.loads("".join([line for line in file_input]))
    elif _is_valid_yaml(file_input):
        data=file_input.read()
        content_type="application/yaml"
    else:
        raise typer.BadParameter("Input file is neither valid JSON nor YAML.")

    r = client.post("api/v1/workflows", data=data, content_type=content_type)
