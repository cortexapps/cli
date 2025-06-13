from cortexapps_cli.command_options import CommandOptions
from cortexapps_cli.command_options import ListCommandOptions
from cortexapps_cli.utils import print_output_with_context, print_output
from rich import print_json
from typing_extensions import Annotated
import json
import typer
import re
from urllib.error import HTTPError

app = typer.Typer(
    help="Plugins commands",
    no_args_is_help=True
)

@app.command()
def list(
    ctx: typer.Context,
    include_drafts: bool = typer.Option(False, "--include-drafts", "-i", help="Also include plugins that are in draft mode"),
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
    Retrieve a list of all plugins, excluding drafts
    """

    client = ctx.obj["client"]

    params = {
       "page": page,
       "pageSize": page_size
    }       

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

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
        r = client.fetch("api/v1/plugins", params=params)
    else:
        # if page is specified, we want to fetch only that page
        r = client.get("api/v1/plugins", params=params)

    if _print:
        data = r
        print_output_with_context(ctx, data)
    else:
        return(r)

@app.command()
def create(
    ctx: typer.Context,
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File containing contents of plugin using schema defined at https://docs.cortex.io/docs/api/create-plugin")] = None,
    force: bool = typer.Option(False, "--force", help="Recreate entity if it already exists."),
):
    """
    Create a new plugin
    """

    client = ctx.obj["client"]
    
    data = json.loads(file_input.read())

    if force:
        plugins = list(ctx, _print=False)
        plugin_tags = [plugin["tag"] for plugin in plugins["plugins"]]

        tag = data['tag']
        if tag in plugin_tags:
            # Remove the 'tag' attribute if it exists
            data.pop("tag", None)
            r = client.put("api/v1/plugins/" + tag, data, raw_response=True)
    else:
        r = client.post("api/v1/plugins", data, raw_response=True)

@app.command()
def delete(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity.")
):
    """
    Delete a plugin by tag
    """

    client = ctx.obj["client"]
    
    client.delete("api/v1/plugins/" + tag_or_id)

@app.command()
def get(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    include_blob: bool = typer.Option(False, "--include-blob", "-i", help="When true, returns the plugin blob.  Defaults to false."),
    _print: bool = typer.Option(True, "--print", help="If result should be printed to the terminal", hidden=True),
):
    """
    Retrieve the metadata of a plugin by tag
    """

    client = ctx.obj["client"]

    params = {
       "includeBlob": include_blob,
    }       
    
    r = client.get("api/v1/plugins/" + tag_or_id, params=params)
    if _print:
        print_json(data=r)
    else:
        # Optionally replace raw newlines inside known problem keys
        #fixed = str(r).replace('\n', '\\n')  # crude but often works

        #data = json.loads(fixed)
        #return(json.dumps(data, indent=2))
        #raw_text = r.text

        # Replace unescaped newlines inside string values with escaped \n
        # WARNING: This is a heuristic and assumes newlines only appear in strings
        #safe_text = re.sub(r'(?<!\\)\n', r'\\n', raw_text)

        #data = json.loads(safe_text)  # Now safe to load
        return(json.dumps(r, indent=2))

@app.command()
def replace(
    ctx: typer.Context,
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File containing contents of plugin using schema defined at https://docs.cortex.io/docs/api/create-plugin")] = None,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity.")
):
    """
    Replace an existing plugin by tag
    """

    client = ctx.obj["client"]
    
    client.put("api/v1/plugins/"+ tag_or_id, data=file_input.read())
