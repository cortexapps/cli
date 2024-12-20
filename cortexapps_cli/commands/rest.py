import json
import yaml
import sys
from typing import List, Optional

import typer
from typing_extensions import Annotated

from rich import print_json
app = typer.Typer(help="REST API commands", no_args_is_help=True)

def parse_multi_value_option(option: List[str] | None) -> dict:
    if option is None:
        return {}
    try:
        return dict([param.split('=') for param in option])
    except:
        raise typer.BadParameter("Invalid parameter format, use Name=value")

def guess_content_type(data: str) -> str:
    try:
        json.loads(data)
        return 'application/json'
    except json.JSONDecodeError:
        try:
            yaml_data = yaml.safe_load(data)
            if isinstance(yaml_data, dict):
                if 'openapi' in yaml_data:
                    return 'application/openapi;charset=utf-8'
                return 'application/yaml'
            return 'text/plain'
        except yaml.YAMLError:
            return 'text/plain'

class RawCommandOptions:
    endpoint = typer.Option(..., "--endpoint", "-e", help="API endpoint", show_default=False)
    headers = Annotated[
        Optional[List[str]],
        typer.Option("--headers", "-H", help="Headers to include in the request, in the format HeaderName=value", show_default=False)
    ]
    params = Annotated[Optional[List[str]], typer.Option("--params", "-P", help="Parameters to include in the request, in the format ParamName=value", show_default=False)]
    input_file = Annotated[typer.FileText, typer.Option("--file", "-f", help="File to read the request body from, use - for stdin")]
    content_type = typer.Option(None, "--content-type", "-c", help="Content type of the request body (leave blank to guess)")


@app.command()
def get(
    ctx: typer.Context,
    endpoint: str = RawCommandOptions.endpoint,
    headers: RawCommandOptions.headers = [],
    params: RawCommandOptions.params = [],
):
    """
    Make a GET request to the API
    """
    req_headers = parse_multi_value_option(headers)
    req_params = parse_multi_value_option(params)
    client = ctx.obj["client"]
    r = client.get(endpoint, headers=req_headers, params=req_params)
    print_json(data=r)

@app.command()
def fetch(
    ctx: typer.Context,
    endpoint: str = RawCommandOptions.endpoint,
    headers: RawCommandOptions.headers = [],
    params: RawCommandOptions.params = [],
):
    """
    Make a GET request to the API, and automatically fetch all pages
    """
    req_headers = parse_multi_value_option(headers)
    req_params = parse_multi_value_option(params)
    client = ctx.obj["client"]
    r = client.fetch(endpoint, headers=req_headers, params=req_params)
    print_json(json.dumps(r))

@app.command()
def delete(
    ctx: typer.Context,
    endpoint: str = RawCommandOptions.endpoint,
    headers: RawCommandOptions.headers = [],
    params: RawCommandOptions.params = [],
):
    """
    Make a DELETE request to the API
    """
    req_headers = parse_multi_value_option(headers)
    req_params = parse_multi_value_option(params)
    client = ctx.obj["client"]
    r = client.delete(endpoint, headers=req_headers, params=req_params)
    if (r):
        print_json(json.dumps(r))

@app.command()
def post(
    ctx: typer.Context,
    endpoint: str = RawCommandOptions.endpoint,
    headers: RawCommandOptions.headers = [],
    params: RawCommandOptions.params = [],
    content_type: str = RawCommandOptions.content_type,
    input: RawCommandOptions.input_file = '-'
):
    """
    Make a POST request to the API
    """
    req_headers = parse_multi_value_option(headers)
    req_params = parse_multi_value_option(params)
    client = ctx.obj["client"]
    data = "".join([line for line in input])
    content_type = content_type or guess_content_type(data)
    r = client.post(endpoint, headers=req_headers, params=req_params, data=data, raw_body=True, content_type=content_type)
    if input == sys.stdin and sys.stdin.isatty() and sys.stdout.isatty():
        print("")
    print_json(json.dumps(r))

@app.command()
def put(
    ctx: typer.Context,
    endpoint: str = RawCommandOptions.endpoint,
    headers: RawCommandOptions.headers = [],
    params: RawCommandOptions.params = [],
    content_type: str = RawCommandOptions.content_type,
    input: RawCommandOptions.input_file = '-'
):
    """
    Make a PUT request to the API
    """
    req_headers = parse_multi_value_option(headers)
    req_params = parse_multi_value_option(params)
    client = ctx.obj["client"]
    data = "".join([line for line in input])
    content_type = content_type or guess_content_type(data)
    r = client.put(endpoint, headers=req_headers, params=req_params, data=data, raw_body=True, content_type=content_type)
    if input == sys.stdin and sys.stdin.isatty() and sys.stdout.isatty():
        print("")
    print_json(json.dumps(r))
