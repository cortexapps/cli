"""
Tests for teams commands.
"""
from cortexapps_cli.cortex import cli

import json
import sys

def _teams_list(capsys):
    cli(["teams", "list"])
    out, err = capsys.readouterr()
    json_data = json.loads(out)

    return json_data

def _catalog_list(capsys):
    cli(["catalog", "list"])
    out, err = capsys.readouterr()
    json_data = json.loads(out)

    return json_data

def test_teams(capsys):
    # Not sure why teams are created both as teams and catalog entities.  Probably part of the
    # teams-as-entities migration.
    json_data = _teams_list(capsys)
    if any(team['teamTag'] == 'test-team' for team in json_data['teams']):
        cli(["teams", "delete", "-t", "test-team"])
    json_data = _catalog_list(capsys)
    if any(entity['tag'] == 'test-team' for entity in json_data['entities']):
        cli(["catalog", "delete", "-t", "test-team"])

    cli(["teams", "create", "-f", "tests/test_teams.yaml"])
    cli(["teams", "get", "-t", "test-team"])
    cli(["teams", "update-metadata", "-t", "test-team", "-f", "tests/test_teams_update.json"])
    cli(["teams", "archive", "-t", "test-team"])
    cli(["teams", "unarchive", "-t", "test-team"])
    cli(["teams", "list"])
    cli(["teams", "delete", "-t", "test-team"])
