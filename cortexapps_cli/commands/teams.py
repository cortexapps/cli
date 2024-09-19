from typing import Optional
from typing_extensions import Annotated
import typer
import json
from rich import print, print_json
from enum import Enum

from cortexapps_cli.models.team import Team

app = typer.Typer()

class TeamType(str, Enum):
    CORTEX = "CORTEX"
    IDP = "IDP"

@app.command()
def create(
    ctx: typer.Context,
    team_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File to read the team definition from")] = None,
    tag: str = typer.Option(None, "--tag", "-t", help="Team tag"),
    type: TeamType = typer.Option(TeamType.CORTEX, "--type", "-y", help="Team type"),
    name: str = typer.Option(None, "--name", "-n", help="Team name"),
    description: str = typer.Option(None, "--description", "-d", help="Team description"),
    summary: str = typer.Option(None, "--summary", "-s", help="Team summary"),
    idp_group: str = typer.Option(None, "--idp-group", "-g", help="IDP group - required when type is IDP"),
    idp_provider: str = typer.Option(None, "--idp-provider", "-p", help="IDP provider - required when type is IDP"),
):
    """
    Create a team

    Use -f to specify a file to read the team definition from (use -f - to read from stdin.) Or, provide the team attributes directly via the command options.
    """
    client = ctx.obj["client"]
    if team_input:
        if tag or name or description or summary or idp_group or idp_provider:
            raise typer.BadParameter("When providing a team definition file, do not specify any other team attributes")
        data = json.loads("".join([line for line in team_input]))
    else:
        if not tag:
            raise typer.BadParameter("tag is required if team definition is not provided")
        if not name:
            raise typer.BadParameter("name is required if team definition is not provided")

        data = {
            "type": type,
            "teamTag": tag,
            "links": [],
            "metadata": {
                "name": name,
            },
            "slackChannels": [],
            "cortexTeam": {
                "members": []
            },
        }

        if description:
            data["metadata"]["description"] = description

        if summary:
            data["metadata"]["summary"] = summary

        if type == TeamType.IDP:
            if not idp_group:
                raise typer.BadParameter("idp-group is required when type is IDP")
            if not idp_provider:
                raise typer.BadParameter("idp-provider is required when type is IDP")
            data["idpGroup"] = {
                "group": idp_group,
                "provider": idp_provider,
            }

    r = client.post("api/v1/teams", data=data)
    print_json(json.dumps(r))

@app.command()
def list(
    ctx: typer.Context,
    include_teams_without_members: bool = typer.Option(False, "--include-teams-without-members", help="Include teams without members"),
):
    """
    List teams

    Provide a team tag to list one team, or list all teams if no tag is provided.
    """
    client = ctx.obj["client"]
    params = {
        "includeTeamsWithoutMembers": include_teams_without_members,
    }
    r = client.get("api/v1/teams", params=params)
    print_json(json.dumps(r))

@app.command()
def get(
    ctx: typer.Context,
    team_tag: str = typer.Option(..., "--team-tag", "-t", help="Team tag"),
):
    """
    Get a team
    """
    client = ctx.obj["client"]
    r = client.get(f"api/v1/teams/{team_tag}")
    print_json(json.dumps(r))

@app.command()
def delete(
    ctx: typer.Context,
    team_tag: str = typer.Option(..., "--team-tag", "-t", help="Team tag"),
):
    """
    Delete a team
    """
    client = ctx.obj["client"]
    client.delete(f"api/v1/teams/{team_tag}")

@app.command()
def archive(
    ctx: typer.Context,
    team_tag: str = typer.Option(..., "--team-tag", "-t", help="Team tag"),
):
    """
    Archive a team
    """
    client = ctx.obj["client"]
    r = client.put(f"api/v1/teams/{team_tag}/archive")
    print_json(json.dumps(r))

@app.command()
def unarchive(
    ctx: typer.Context,
    team_tag: str = typer.Option(..., "--team-tag", "-t", help="Team tag"),
):
    """
    Unarchive a team
    """
    client = ctx.obj["client"]
    r = client.put(f"api/v1/teams/{team_tag}/unarchive")
    print_json(json.dumps(r))

@app.command()
def update(
    ctx: typer.Context,
    team_tag: str = typer.Option(..., "--team-tag", "-t", help="The tag of the team to update"),
    team_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File to read the team definition from")] = None,
    name: str = typer.Option(None, "--name", "-n", help="Team name"),
    description: str = typer.Option(None, "--description", "-d", help="Team description"),
    summary: str = typer.Option(None, "--summary", "-s", help="Team summary"),
):
    """
    Update team
    """
    client = ctx.obj["client"]
    if team_input:
        if name or description or summary:
            raise typer.BadParameter("When providing a team definition file, do not specify any other team attributes")
        team = Team.from_json("".join([line for line in team_input]))
    else:
        team = Team.from_obj(client.get(f"api/v1/teams/{team_tag}"))
        if name:
            team.metadata.name = name
        if description:
            team.metadata.description = description
        if summary:
            team.metadata.summary = summary
    r = client.put(f"api/v1/teams/{team_tag}", data=team.to_obj())
    print_json(json.dumps(r))

@app.command("update-metadata")
def update_metadata(
    ctx: typer.Context,
    team_tag: str = typer.Option(..., "--team-tag", "-t", help="The tag of the team to update"),
    team_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File to read the team definition from")] = None,
):
    """
    Update team metadata
    """

    # all the update methods seem to do the same thing when reading from a file
    update(ctx, team_tag=team_tag, team_input=team_input, name=None, description=None, summary=None)

@app.command("update-members")
def update_members(
    ctx: typer.Context,
    team_tag: str = typer.Option(..., "--team-tag", "-t", help="The tag of the team to update"),
    team_input: Annotated[typer.FileText, typer.Option("--file", "-f", help="File to read the team definition from")] = None,
):
    """
    Update team members
    """

    # all the update methods seem to do the same thing when reading from a file
    update(ctx, team_tag=team_tag, team_input=team_input, name=None, description=None, summary=None)
