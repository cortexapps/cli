import typer

app = typer.Typer(help="IP Allowlist commands", no_args_is_help=True)

@app.command()
def get(
    ctx: typer.Context,
    page: int | None = typer.Option(None, "--page", "-p", help="Page number to return, 0 indexed - omit to fetch all pages"),
    page_size: int | None = typer.Option(None, "--page-size", "-z", help="Page size for results"),
):
    """
    Get allowlist of IP addresses & ranges
    """

    client = ctx.obj["client"]

    params = {
       "page": page,
       "pageSize": page_size
    }       

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}
    
    client.fetch_or_get("api/v1/ip-allowlist", page, params=params)

@app.command()
def replace(
    ctx: typer.Context,
    addresses: str = typer.Option(..., "--address", "-a", help="Comma-delimited list of IP addresses and/or IP ranges of form ipAddress[:description], for example 127.0.0.1:'my local IP'"),
    force: bool = typer.Option(False, "--force", "-o", help="When true, entries will be updated even if the list doesn't contain the requestor's IP address")
):
    """
    Replace existing allowlist with provided list of IP addresses & ranges
    """

    client = ctx.obj["client"]

    data = {
            "entries": [{"address": x.split(':')[0], "description": None if len(x.split(':')) < 2 else x.split(':')[1]} for x in addresses.split(',')]
    }

    params = {
        "force": force,
    }

    r = client.put("api/v1/ip-allowlist", data=data, params=params)

    print_json(data=r)


@app.command()
def validate(
    ctx: typer.Context,
    addresses: str = typer.Option(..., "--address", "-a", help="Comma-delimited list of IP addresses and/or IP ranges of form ipAddress[:description], for example 127.0.0.1:'my local IP'")
):
    """
    Validates allowlist of IP addresses & ranges
    """

    client = ctx.obj["client"]

    data = {
            "entries": [{"address": x.split(':')[0], "description": None if len(x.split(':')) < 2 else x.split(':')[1]} for x in addresses.split(',')]
    }

    r = client.post("api/v1/ip-allowlist/validate", data=data)

    print_json(data=r)

@app.command()
def remove_all(
    ctx: typer.Context,
):
    """
    Remove all entries from allowlist
    """

    client = ctx.obj["client"]

    data = {
            "entries": []
    }

    r = client.put("api/v1/ip-allowlist", data=data)

    print_json(data=r)
