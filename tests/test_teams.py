"""
Tests for teams commands.
"""
from cortexapps_cli.cortex import cli

import json

def test_teams_create(capsys):
    cli(["teams", "list"])
    out, err = capsys.readouterr()
    json_data = json.loads(out)

    cli(["catalog", "list"])
    out, err = capsys.readouterr()
    catalog_json_data = json.loads(out)

    if any(team['teamTag'] == 'cli-test-team' for team in json_data['teams']):
        cli(["teams", "delete", "-t", "cli-test-team"])

    if any(entity['tag'] == 'cli-test-team' for entity in catalog_json_data['entities']):
        cli(["catalog", "delete", "-t", "cli-test-team"])

    cli(["teams", "create", "-f", "tests/test_teams.yaml"])

def test_teams_get():
    cli(["teams", "get", "-t", "test-team-1"])

def test_teams_list():
    cli(["teams", "list"])

def test_teams_archive():
    cli(["teams", "archive", "-t", "test-team-1"])
    cli(["teams", "unarchive", "-t", "test-team-1"])

def test_teams_update_metadata():
    cli(["teams", "update-metadata", "-t", "test-team-2", "-f", "tests/test_teams_update.json"])
