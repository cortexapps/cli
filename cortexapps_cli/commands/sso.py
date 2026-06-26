import typer
import json
from enum import Enum
from typing_extensions import Annotated
from cortexapps_cli.utils import print_output_with_context

app = typer.Typer(
    help="SSO configuration commands",
    no_args_is_help=True
)

GOOGLE_ISSUER = "https://accounts.google.com"

class Provider(str, Enum):
    OKTA = "OKTA"
    GOOGLE = "GOOGLE"
    AZURE = "AZURE"

@app.command()
def list(
    ctx: typer.Context,
):
    """List all SSO configurations."""
    client = ctx.obj["client"]
    r = client.get("api/v1/sso/configurations")
    print_output_with_context(ctx, r)

@app.command()
def create(
    ctx: typer.Context,
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="JSON file containing OIDC configuration; use -f- for stdin")] = None,
    provider: Provider = typer.Option(None, "--provider", "-p", help="SSO provider: OKTA, GOOGLE, or AZURE"),
    identifier: str = typer.Option(None, "--identifier", "-i", help="Client ID from the identity provider"),
    secret: str = typer.Option(None, "--secret", "-s", help="Client secret from the identity provider"),
    issuer: str = typer.Option(None, "--issuer", help="Issuer URI (auto-filled for Google)"),
):
    """Create an OIDC SSO connection.

    Provide either a JSON file (-f) or command-line parameters (--provider, --identifier, --secret).

    Examples:

        cortex sso create --provider okta --identifier <client-id> --secret <secret> --issuer https://myorg.okta.com

        cortex sso create --provider google --identifier <client-id> --secret <secret>

        cortex sso create -f oidc-config.json
    """
    client = ctx.obj["client"]

    if file_input:
        if provider or identifier or secret or issuer:
            raise typer.BadParameter("When providing a JSON file, do not specify --provider, --identifier, --secret, or --issuer")
        data = json.loads("".join([line for line in file_input]))
    else:
        if not provider:
            raise typer.BadParameter("--provider is required when not using -f")
        if not identifier:
            raise typer.BadParameter("--identifier is required when not using -f")
        if not secret:
            raise typer.BadParameter("--secret is required when not using -f")

        if provider == Provider.GOOGLE:
            issuer_uri = GOOGLE_ISSUER
        elif issuer:
            issuer_uri = issuer
        else:
            raise typer.BadParameter("--issuer is required for OKTA and AZURE providers")

        data = {
            "type": "client_secret_basic",
            "id": identifier,
            "secret": secret,
            "issuerUri": issuer_uri,
            "connectionType": provider.value,
        }

    r = client.post("api/v1/sso/oidc/configurations", data=data)
    print_output_with_context(ctx, r)

@app.command()
def delete(
    ctx: typer.Context,
    connection_id: str = typer.Option(..., "--connection-id", "-c", help="The connection ID to delete"),
):
    """Delete an SSO connection by connection ID."""
    client = ctx.obj["client"]
    r = client.delete("api/v1/sso/configurations/" + connection_id)
    print_output_with_context(ctx, r)

@app.command()
def delete_all(
    ctx: typer.Context,
):
    """Delete all SSO configurations."""
    client = ctx.obj["client"]
    r = client.delete("api/v1/sso/configurations")
    print_output_with_context(ctx, r)
