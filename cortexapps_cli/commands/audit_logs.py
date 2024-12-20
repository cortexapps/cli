from datetime import datetime
from enum import Enum
import typer

app = typer.Typer(help="Audit log commands", no_args_is_help=True)

class Action(str, Enum):
    CREATE = "CREATE"
    DELETE = "DELETE"
    UPDATE = "UPDATE"

class ActorType(str, Enum):
    ANONYMOUS = "ANONYMOUS"
    API_KEY = "API_KEY"
    BACKSTAGE = "BACKSTAGE"
    OAUTH2 = "OAUTH2"
    PERSONAL_API_KEY = "PERSONAL_API_KEY"

class ActorRequestType(str, Enum):
    API_KEY_ENTITY = "API_KEY_ENTITY"
    ATLASSIAN_WEBHOOK = "ATLASSIAN_WEBHOOK"
    SCORECARD_BADGES = "SCORECARD_BADGES"
    SLACK_COMMAND = "SLACK_COMMAND"

@app.command()
def get(
    ctx: typer.Context,
    actions: list[Action] | None = typer.Option(None, "--actions", "-a", help="The audit action"),
    actorApiKeyIdentifiers: list[str] | None = typer.Option(None, "--actorApiKeyIdentifiers", "-ak", help="API key name associated with audit event"),
    actorEmails: list[str] | None = typer.Option(None, "--actorEmails", "-ae", help="Email address associated with audit event"),
    actorIpAddresses: list[str] | None = typer.Option(None, "--actorIpAddresses", "-ai", help="Source IP Addresses associated with audit event"),
    actorRequestTypes: list[ActorRequestType] | None = typer.Option(None, "--actorRequestTypes", "-ar", help="Request event associated with audit event"),
    actorTypes: list[ActorType] | None = typer.Option(None, "--actorTypes", "-at", help="Actor that triggered the audit event"),
    end_time: datetime = typer.Option(None, "--endTime", "-e", help="End time of audit logs to retrieve", formats=["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"]),
    objectIdentifiers: list[str] | None = typer.Option(None, "--objectIdentifiers", "-oi", help="The name of the Cortex object that was modified, ie x-cortex-tag value, metadata field name, etc."),
    objectTypes: list[str] | None = typer.Option(None, "--objectTypes", "-ot", help="ObjectTypes"),
    page: int | None = typer.Option(None, "--page", "-p", help="Page number to return, 0 indexed - omit to fetch all pages"),
    page_size: int | None = typer.Option(None, "--page-size", "-z", help="Page size for results"),
    start_time: datetime = typer.Option(None, "--startTime", "-s", help="Start time of audit logs to retrieve", formats=["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"]),
):
    """
    Note: To see the complete list of possible values, please reference the available filter options for audit logs under Settings in the app.
    """
    client = ctx.obj["client"]

    params = {
        "actions": actions,
        "actorApiKeyIdentifiers": actorApiKeyIdentifiers,
        "actorEmails": actorEmails,
        "actorIpAddresses": actorIpAddresses,
        "actorRequestTypes": actorRequestTypes,
        "actorTypes": actorTypes,
        "endTime": end_time,
        "objectIdentifiers": objectIdentifiers,
        "objectTypes": objectTypes,
        "page": page,
        "pageSize": page_size,
        "startTime": start_time
    }

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    # convert datetime and list types to string
    for k, v in params.items():
        if str(type(v)) == "<class 'datetime.datetime'>":
           params[k] = v.strftime('%Y-%m-%dT%H:%M:%S')
        if str(type(v)) == "<class 'list'>":
            params[k] = ','.join(v)

    client.fetch_or_get("api/v1/audit-logs", page, params=params)
