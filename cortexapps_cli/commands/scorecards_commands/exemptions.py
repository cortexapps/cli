import json
from enum import Enum
from rich import print_json
import typer
from typing_extensions import Annotated
from cortexapps_cli.command_options import ListCommandOptions
from cortexapps_cli.utils import print_output_with_context

app = typer.Typer(help="Exemptions commands", no_args_is_help=True)

class Status(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"

@app.command(name="list")
def list_exemptions(
    ctx: typer.Context,
    scorecard_tag: str = typer.Option(None, "--scorecard-tag", "-s", help="Only return exemptions for the Scorecard with this tag"),
    entity_tag: str = typer.Option(None, "--entity-tag", "-e", help="Only return exemptions for the entity with this tag (x-cortex-tag)"),
    rule_identifier: str = typer.Option(None, "--rule-id", "-ri", help="Only return exemptions for the rule with this identifier; requires --scorecard-tag"),
    status: Status = typer.Option(None, "--status", "-st", help="Only return exemptions with this status; APPROVED excludes approvals past their end date, which are returned as EXPIRED"),
    requester_email: str = typer.Option(None, "--requester-email", "-re", help="Only return exemptions requested by the user with this email"),
    approver_email: str = typer.Option(None, "--approver-email", "-ae", help="Only return exemptions approved by the user with this email"),
    only_active: bool = typer.Option(False, "--only-active", "-a", help="Only return exemptions that are pending, or approved and not yet expired"),
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
    List Scorecard rule exemptions
    """

    client = ctx.obj["client"]

    params = {
       "scorecardTag": scorecard_tag,
       "entityTag": entity_tag,
       "ruleIdentifier": rule_identifier,
       "status": status.value if status else None,
       "requesterEmail": requester_email,
       "approverEmail": approver_email,
       "onlyActive": "true" if only_active else None,
       "page": page,
       "pageSize": page_size,
    }

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    if (table_output or csv_output) and not ctx.params.get('columns'):
        ctx.params['columns'] = [
            "ID=id",
            "Scorecard=scorecardTag",
            "Rule=ruleIdentifier",
            "Entity=entityTag",
            "Status=exemptionStatus.status",
            "Requester=requestedBy.email",
            "EndDate=endDate",
        ]

    if page is None:
        # if page is not specified, we want to fetch all pages
        r = client.fetch("api/v1/scorecards/exemptions", params=params)
    else:
        # if page is specified, we want to fetch only that page
        r = client.get("api/v1/scorecards/exemptions", params=params)

    print_output_with_context(ctx, r)

@app.command()
def request(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    scorecard_tag: str = typer.Option(..., "--scorecard-tag", "-s", help="Unique tag for the scorecard"),
    days: int = typer.Option(0, "--days", "-d", help="Number of days that rule should be exempt. If not set, rule will be exempt until revoked."),
    reason: str = typer.Option(..., "--reason", "-r", help="Reason for creating exemption"),
    rule_identifier: str = typer.Option(..., "--rule-id", "-ri", help="Identifier of the Scorecard rule to request exemption for"),
):
    """
    Request Scorecard rule exemption
    """

    client = ctx.obj["client"]

    data = {
       "days": days,
       "reason": reason,
       "ruleIdentifier": rule_identifier
    }       
    
    r = client.post("api/v1/scorecards/" + scorecard_tag + "/entity/" + tag_or_id + "/exemption", data=data)
    print_json(data=r)

@app.command()
def approve(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    scorecard_tag: str = typer.Option(..., "--scorecard-tag", "-s", help="Unique tag for the scorecard"),
    rule_identifier: str = typer.Option(..., "--rule-id", "-ri", help="Identifier of the Scorecard rule to request exemption for"),
):
    """
    Approve Scorecard rule exemption
    """

    client = ctx.obj["client"]

    data = {
       "ruleIdentifier": rule_identifier
    }       
    
    r = client.put("api/v1/scorecards/" + scorecard_tag + "/entity/" + tag_or_id + "/exemption/approve", data=data)
    print_json(data=r)

@app.command()
def deny(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    scorecard_tag: str = typer.Option(..., "--scorecard-tag", "-s", help="Unique tag for the scorecard"),
    rule_identifier: str = typer.Option(..., "--rule-id", "-ri", help="Identifier of the Scorecard rule to request exemption for"),
    reason: str = typer.Option(..., "--reason", "-r", help="Reason for creating exemption"),
):
    """
    Deny Scorecard rule exemption
    """

    client = ctx.obj["client"]

    data = {
       "ruleIdentifier": rule_identifier,
       "reason": reason
    }       
    
    r = client.put("api/v1/scorecards/" + scorecard_tag + "/entity/" + tag_or_id + "/exemption/deny", data=data)
    print_json(data=r)

@app.command()
def revoke(
    ctx: typer.Context,
    tag_or_id: str = typer.Option(..., "--tag-or-id", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    scorecard_tag: str = typer.Option(..., "--scorecard-tag", "-s", help="Unique tag for the scorecard"),
    reason: str = typer.Option(..., "--reason", "-r", help="Reason for creating exemption"),
    rule_identifier: str = typer.Option(..., "--rule-id", "-ri", help="Identifier of the Scorecard rule to request exemption for"),
):
    """
    Revoke Scorecard rule exemption
    """

    client = ctx.obj["client"]

    data = {
       "reason": reason,
       "ruleIdentifier": rule_identifier
    }       
    
    r = client.put("api/v1/scorecards/" + scorecard_tag + "/entity/" + tag_or_id + "/exemption/revoke", data=data)
    print_json(data=r)
