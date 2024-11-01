#from collections import defaultdict
from enum import Enum
import json
from rich import print_json
import typer

app = typer.Typer(help="GitOps Logs commands")

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
    page: int | None = typer.Option(None, "--page", "-p", help="Page number to return, 0 indexed - omit to fetch all pages"),
    page_size: int | None = typer.Option(None, "--page-size", "-z", help="Page size for results"),
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
    
    if page is None:
        # if page is not specified, we want to fetch all pages
        r = client.fetch("api/v1/gitops-logs", params=params)
    else:
        # if page is specified, we want to fetch only that page
        r = client.get("api/v1/gitops-logs", params=params)

    print_json(data=r)
