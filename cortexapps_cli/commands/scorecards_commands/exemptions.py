import json
from rich import print_json
import typer
from typing_extensions import Annotated

app = typer.Typer(help="Exemptions commands", no_args_is_help=True)

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
