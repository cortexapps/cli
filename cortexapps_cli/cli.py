#!/usr/bin/env python3

import typer
from typing_extensions import Annotated

import os
import sys
import importlib.metadata
import tomllib
import configparser
import logging
import webbrowser
import requests

from cortexapps_cli.cortex_client import CortexClient

import cortexapps_cli.commands.api_keys as api_keys
import cortexapps_cli.commands.audit_logs as audit_logs
import cortexapps_cli.commands.backup as backup
import cortexapps_cli.commands.catalog as catalog
import cortexapps_cli.commands.custom_data as custom_data
import cortexapps_cli.commands.custom_events as custom_events
import cortexapps_cli.commands.custom_metrics as custom_metrics
import cortexapps_cli.commands.dependencies as dependencies
import cortexapps_cli.commands.deploys as deploys
import cortexapps_cli.commands.discovery_audit as discovery_audit
import cortexapps_cli.commands.docs as docs
import cortexapps_cli.commands.entity_types as entity_types
import cortexapps_cli.commands.entity_relationship_types as entity_relationship_types
import cortexapps_cli.commands.entity_relationships as entity_relationships
import cortexapps_cli.commands.gitops_logs as gitops_logs
import cortexapps_cli.commands.groups as groups
import cortexapps_cli.commands.initiatives as initiatives
import cortexapps_cli.commands.integrations as integrations
import cortexapps_cli.commands.ip_allowlist as ip_allowlist
import cortexapps_cli.commands.on_call as on_call
import cortexapps_cli.commands.packages as packages
import cortexapps_cli.commands.plugins as plugins
import cortexapps_cli.commands.queries as queries
import cortexapps_cli.commands.rest as rest
import cortexapps_cli.commands.scim as scim
import cortexapps_cli.commands.scorecards as scorecards
import cortexapps_cli.commands.secrets as secrets
import cortexapps_cli.commands.solutions as solutions
import cortexapps_cli.commands.teams as teams
import cortexapps_cli.commands.users as users
import cortexapps_cli.commands.workflows as workflows

class _SortedTyper(typer.Typer):
    """Typer subclass that sorts all commands alphabetically in --help output."""
    def __call__(self, *args, **kwargs):
        import typer.main as _tm
        click_app = _tm.get_command(self)
        click_app.commands = dict(sorted(click_app.commands.items()))
        return click_app(*args, **kwargs)

app = _SortedTyper(
    no_args_is_help=True,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]}
)

# Commands and subcommands are registered below in alphabetical order.
# Direct commands (login, version) are registered via app.command() calls
# interleaved with add_typer() calls so they appear alphabetically in --help.

# global options
@app.callback()
def global_callback(
    ctx: typer.Context,
    api_key: str = typer.Option(None, "--api-key", "-k", help="API key", envvar="CORTEX_API_KEY"),
    url: str = typer.Option(None, "--url", "-u", help="Base URL for the API", envvar="CORTEX_BASE_URL"),
    config_file: str = typer.Option(os.path.join(os.path.expanduser('~'), '.cortex', 'config'), "--config", "-c", help="Config file path", envvar="CORTEX_CONFIG"),
    tenant: str = typer.Option("default", "--tenant", "-t", help="Tenant alias", envvar="CORTEX_TENANT_ALIAS"),
    log_level: Annotated[str, typer.Option("--log-level", "-l", help="Set the logging level")] = "WARNING",
    rate_limit: int = typer.Option(None, "--rate-limit", "-r", help="API rate limit in requests per minute (default: 1000)", envvar="CORTEX_RATE_LIMIT")
):
    if not ctx.obj:
        ctx.obj = {}

    # Store config file path and tenant for use by the login command
    ctx.obj["config_file"] = config_file
    ctx.obj["tenant"] = tenant

    # login command handles its own auth setup
    if ctx.invoked_subcommand == "login":
        return

    if ctx.invoked_subcommand == "solutions":
        ctx.obj["_auth_params"] = {
            "api_key": api_key,
            "url": url,
            "config_file": config_file,
            "tenant": tenant,
            "log_level": log_level,
            "rate_limit": rate_limit,
        }
        return

    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    if not os.path.isfile(config_file):
        # no config file found
        if not api_key:
            raise typer.BadParameter("No API key provided and no config file found")
        create_config = False

        # check if we are in a terminal, if so, ask the user if they want to create a config file
        if sys.stdin.isatty() and sys.stdout.isatty():
            create_config = typer.confirm("No config file found. Do you want to create one?")

        if create_config:
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, "w") as f:
                f.write(f"[{tenant}]\n")
                f.write(f"api_key = {api_key}\n")
                f.write(f"base_url = {url}\n")
    else:
        # config file found
        # if api_key is provided, use that in preference to the config file
        config = configparser.ConfigParser()
        config.read(config_file)
        if tenant not in config:
            raise typer.BadParameter(f"Tenant {tenant} not found in config file")
        if not api_key:
            api_key = config[tenant]["api_key"]
        if not url:
            if 'base_url' in config[tenant].keys():
                url = config[tenant]['base_url']
            else:
                url = "https://api.getcortexapp.com"

    # Set default URL if not provided
    if not url:
        url = "https://api.getcortexapp.com"

    # strip any quotes or spaces from the api_key and url
    api_key = api_key.strip('"\' ')
    url = url.strip('"\' /')

    ctx.obj["client"] = CortexClient(api_key, tenant, numeric_level, url, rate_limit)

DEFAULT_API_URL = "https://api.getcortexapp.com"
DEFAULT_UI_URL = "https://app.getcortexapp.com"
DEFAULT_UI_KEYS_PATH = "/admin/settings/personal-access-tokens"

def login(
    ctx: typer.Context,
    open_browser: bool = typer.Option(True, "--open-browser/--no-open-browser", help="Open browser to Cortex login page"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing tenant config without prompting"),
):
    """
    Log in to Cortex and save credentials to the config file
    """
    config_file = ctx.obj.get("config_file")

    # Prompt for workspace name — this is both the Cortex workspace slug and the local config alias
    default_tenant = ctx.obj.get("tenant", "default")
    tenant = typer.prompt("Workspace name", default=default_tenant).strip()

    # Prompt for base URL
    url = typer.prompt("Base URL", default=DEFAULT_API_URL).strip('"\' /')

    # Check existing config for this tenant
    config = configparser.ConfigParser()
    if os.path.isfile(config_file):
        config.read(config_file)
        if tenant in config and not force:
            if not typer.confirm(f"Workspace '{tenant}' already exists in config. Overwrite?"):
                raise typer.Abort()

    # Derive UI URL, prefilling the workspace name on the login page
    if url == DEFAULT_API_URL:
        ui_base = DEFAULT_UI_URL
    else:
        ui_base = url.replace("://api.", "://app.")

    pat_url = f"{ui_base}{DEFAULT_UI_KEYS_PATH}?tenantCode={tenant}"

    if open_browser:
        typer.echo(f"\nOpening browser to the Personal Access Tokens page for workspace '{tenant}'.")
        typer.echo(f"Create or copy a personal access token, then come back here and paste it below.\n")
        webbrowser.open(pat_url)
    else:
        typer.echo(f"\nGo to {pat_url} to create or copy a personal access token, then paste it below.\n")

    # Prompt for API key (hidden input)
    api_key = typer.prompt("API key", hide_input=True).strip('"\' ')

    # Validate the key with a lightweight API call
    typer.echo("Validating API key...", nl=False)
    try:
        resp = requests.get(
            f"{url}/api/v1/catalog",
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "cortexapps-cli/login",
            },
            params={"pageSize": 1},
            timeout=10,
        )
        if resp.status_code == 401:
            typer.echo(" invalid.")
            typer.echo("Error: API key was not accepted (HTTP 401). Please check the key and try again.")
            raise typer.Exit(1)
        elif not resp.ok:
            typer.echo(f" failed (HTTP {resp.status_code}).")
            typer.echo(f"Error: Unexpected response from {url}. Please check the URL and try again.")
            raise typer.Exit(1)
        else:
            typer.echo(" OK.")
    except requests.exceptions.ConnectionError:
        typer.echo(" connection failed.")
        typer.echo(f"Error: Could not connect to {url}. Please check the URL and try again.")
        raise typer.Exit(1)
    except requests.exceptions.Timeout:
        typer.echo(" timed out.")
        typer.echo(f"Error: Request to {url} timed out. Please check the URL and try again.")
        raise typer.Exit(1)

    # Write / update config
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    config[tenant] = {"api_key": api_key}
    if url != DEFAULT_API_URL:
        config[tenant]["base_url"] = url

    with open(config_file, "w") as f:
        config.write(f)

    tenant_flag = f" -t {tenant}" if tenant != "default" else ""
    typer.echo(f"\nCredentials saved to {config_file}")
    typer.echo(f"You can now run: cortex{tenant_flag} catalog list")


def version():

    """
    Show the version and exit
    """
    try:
        with open("pyproject.toml", "rb") as f:
            pyproject = tomllib.load(f)
        version = pyproject["tool"]["poetry"]["version"]
    except Exception as e:
        version = importlib.metadata.version('cortexapps_cli')
    print(version)

# Register all commands alphabetically so they appear in order in --help
app.add_typer(api_keys.app, name="api-keys")
app.add_typer(audit_logs.app, name="audit-logs")
app.add_typer(backup.app, name="backup")
app.add_typer(catalog.app, name="catalog")
app.add_typer(custom_data.app, name="custom-data")
app.add_typer(custom_events.app, name="custom-events")
app.add_typer(custom_metrics.app, name="custom-metrics")
app.add_typer(dependencies.app, name="dependencies")
app.add_typer(deploys.app, name="deploys")
app.add_typer(discovery_audit.app, name="discovery-audit")
app.add_typer(docs.app, name="docs")
app.add_typer(entity_relationship_types.app, name="entity-relationship-types")
app.add_typer(entity_relationships.app, name="entity-relationships")
app.add_typer(entity_types.app, name="entity-types")
app.add_typer(gitops_logs.app, name="gitops-logs")
app.add_typer(groups.app, name="groups")
app.add_typer(initiatives.app, name="initiatives")
app.add_typer(integrations.app, name="integrations")
app.add_typer(ip_allowlist.app, name="ip-allowlist")
app.command()(login)
app.add_typer(on_call.app, name="on-call")
app.add_typer(packages.app, name="packages")
app.add_typer(plugins.app, name="plugins")
app.add_typer(queries.app, name="queries")
app.add_typer(rest.app, name="rest")
app.add_typer(scim.app, name="scim")
app.add_typer(scorecards.app, name="scorecards")
app.add_typer(secrets.app, name="secrets")
app.add_typer(solutions.app, name="solutions")
app.add_typer(teams.app, name="teams")
app.add_typer(users.app, name="users")
app.command()(version)
app.add_typer(workflows.app, name="workflows")

if __name__ == "__main__":
    app()
