import base64
import gzip
import json
import typer
from datetime import datetime, timezone
from rich.console import Console
from rich.table import Table
import rich.box

app = typer.Typer(
    help="Show identity and metadata for the currently configured API key",
    no_args_is_help=False,
    invoke_without_command=True,
)

@app.callback(invoke_without_command=True)
def whoami(ctx: typer.Context):
    """Show identity and metadata for the currently configured API key."""
    if ctx.invoked_subcommand is not None:
        return

    client = ctx.obj["client"]
    token = client.api_key

    parts = token.split(".")
    if len(parts) != 3:
        typer.echo("Error: API key is not a valid JWT", err=True)
        raise typer.Exit(1)

    header_b64, payload_b64, _ = parts
    header = json.loads(base64.urlsafe_b64decode(header_b64 + "=="))
    payload_bytes = base64.urlsafe_b64decode(payload_b64 + "==")
    if header.get("zip") == "GZIP":
        payload_bytes = gzip.decompress(payload_bytes)
    claims = json.loads(payload_bytes)

    def fmt_ts(ts):
        if ts is None:
            return "—"
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    rows = [
        ("Base URL",   client.base_url),
        ("Tenant",     client.tenant),
        ("Tenant ID",  str(claims["tenant-id"]) if "tenant-id" in claims else "— (not encoded in token)"),
        ("User ID",    claims.get("sub") or "—"),
        ("Token Type", claims.get("type") or "—"),
        ("Auth Scope", claims.get("key-authenticated-request-type") or "—"),
        ("Issued",     fmt_ts(claims.get("iat"))),
        ("Expires",    fmt_ts(claims.get("exp"))),
        ("Last 4",     token[-4:]),
    ]

    console = Console()
    table = Table(show_header=False, box=rich.box.SIMPLE, padding=(0, 1))
    table.add_column(style="dim", no_wrap=True)
    table.add_column()
    for label, value in rows:
        table.add_row(label, value)
    console.print(table)
