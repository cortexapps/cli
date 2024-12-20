from enum import Enum
import json
from rich import print_json
import typer
import urllib.parse

app = typer.Typer(help="SCIM commands", no_args_is_help=True)

# As of November 2024, sortBy and sortOrder are not supported in our code and result in a 501 error
# Not sure how domain is supposed to be used so leaving it out too
# Couldn't get patch, delete and add to work so leaving them out until I can do further research
@app.command()
def list(
    ctx: typer.Context,
    attributes: str = typer.Option(None, "--attributes", "-a", help="Comma-separated list of attributes to include in response; example: name.familyName,active"),
    count: int | None = typer.Option(None, "--count", "-c", help="Return only the first 'count' results"),
    excluded_attributes: str = typer.Option(None, "--excluded-attributes", "-e", help="Comma-separated list of attributes to exclude from response; example: name.givenName,emails"),
    filter: str = typer.Option(None, "--filter", "-f", help="Filtering only supported for userName, example: 'userName eq anish@cortex.io'"),
    start_index: int | None = typer.Option(None, "--start-index", "-s", help="Return items starting with index number, indexing starts with 1")
):
    """
    Get users based on provided criteria
    """

    client = ctx.obj["client"]

    params = {
       "attributes": attributes,
       "excludedAttributes": excluded_attributes,
       "filter": filter,
       "startIndex": start_index,
       "count": count
    }       

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}
    
    r = client.get("scim/v2/Users", params=urllib.parse.urlencode(params))
    print_json(data=r)

@app.command()
def get(
    ctx: typer.Context,
    attributes: str = typer.Option(None, "--attributes", "-a", help="Comma-separated list of attributes to include in response; example: name.familyName,active"),
    excluded_attributes: str = typer.Option(None, "--excluded-attributes", "-e", help="Comma-separated list of attributes to exclude from response; example: name.givenName,emails"),
    id: str = typer.Option(..., "--id", "-i", help="SCIM id of user to get"),
):
    """
    Gets a user based on id
    """

    client = ctx.obj["client"]

    params = {
       "attributes": attributes,
       "excludedAttributes": excluded_attributes
    }       

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}
    
    r = client.get("scim/v2/Users/" + id, params=urllib.parse.urlencode(params))
    print_json(data=r)

# I get a 403 when testing this in my environment, but leaving in because it's syntactically correct
@app.command()
def delete(
    ctx: typer.Context,
    id: str = typer.Option(..., "--id", "-i", help="SCIM id of user to delete"),
):
    """
    Delete a user based on id
    """

    client = ctx.obj["client"]
    
    r = client.delete("scim/v2/Users/" + id)
