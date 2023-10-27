"""
Tests for teams commands.
"""
from cortexapps_cli.cortex import cli

def test_teams_create(capsys):
    cli(["teams", "delete", "-t", "test-team"])
    out, err = capsys.readouterr()
    if (str(out).find('{"teamTag":"test-team"') != -1):
        cli(["teams", "delete", "-t", "test-team"])
    cli(["teams", "create", "-f", "tests/test_teams.yaml"])

def test_teams_get():
    cli(["teams", "get", "-t", "test-team"])

def test_teams_list():
    cli(["teams", "list"])

def test_teams_archive():
    cli(["teams", "archive", "-t", "test-team"])

def test_teams_unarchive():
    cli(["teams", "unarchive", "-t", "test-team"])

def test_teams_update_metadata():
    cli(["teams", "update-metadata", "-t", "test-team", "-f", "tests/test_teams_update.json"])
