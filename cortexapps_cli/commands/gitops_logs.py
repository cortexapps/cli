from enum import Enum
#import json
#from rich import print_json
import typer
from cortexapps_cli.command_options import ListCommandOptions
from cortexapps_cli.utils import print_output_with_context

app = typer.Typer(
    help="GitOps Logs commands",
    no_args_is_help=True
)

class Operation(str, Enum):
    ARCHIVED = "ARCHIVED"
    CREATED = "CREATED"
    NO_CHANGE = "NO_CHANGE"
    UPDATED = "UPDATED"

@app.command()
def get(
    ctx: typer.Context,
    file: str = typer.Option(None, "--file", "-f", help="File name within the repository"),
    file_name: str = typer.Option(None, "--file-name", "-fn", help="File name within the repository; TODO: what is difference with this and file parm?"),
    repository: str = typer.Option(None, "--repository", "-r", help="Repository name as defined in your Git provider"),
    sha: str = typer.Option(None, "--sha", "-s", help="Commit SHA"),
    operation: Operation = typer.Option(None, "--operation", "-o", help="One of CREATED, UPDATED, ARCHIVED, NO_CHANGE"),
    error_only: bool = typer.Option(False, "--error-only", "-eo", help="Only include entries with errors"),
    #page: int | None = typer.Option(None, "--page", "-p", help="Page number to return, 0 indexed - omit to fetch all pages"),
    #page_size: int | None = typer.Option(None, "--page-size", "-z", help="Page size for results"),
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
    Retrieve GitOps logs.  API key must have the 'View GitOps logs' permission.
    """

    client = ctx.obj["client"]

    params = {
       "errorOnly": error_only,
       "file": file,
       "fileName": file_name,
       "operation": operation,
       "page": page,
       "pageSize": page_size,
       "repository": repository,
       "sha": sha
    }       

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    if (table_output or csv_output) and not ctx.params.get('columns'):
        ctx.params['columns'] = [
            "Files=files",
            "repositoryName=repository.repositoryName",
            "provider=repository.provider",
            "Commit=commit",
            "Date=dateCreated",
        ]
    
    #prt = True
    #client.fetch_or_get("api/v1/gitops-logs", page, prt, params=params)
    if page is None:
        r = client.fetch("api/v1/gitops-logs", params=params)
    else:
        r = client.get("api/v1/gitops-logs", params=params)

    print_output_with_context(ctx, r)
