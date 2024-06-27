"""
Tests for teams commands.
"""
from cortexapps_cli.cortex import cli

import json
import sys

# Deleted this test for several reasons:
#
# 1. It's failing in release.com environments.
# 2. There appears to be a bug where teams created using the teams API are not immediately
#    avaialble from teams list API.
# 3. There are plans to deprecate the teams API and manage everything with the catalog API.
# 4. You can create Cortex-managed teams with the catalog API.
# 
# def test_teams_create(capsys):
#     cli(["teams", "list"])
#     out, err = capsys.readouterr()
#     json_data = json.loads(out)
# 
#     cli(["catalog", "list"])
#     out, err = capsys.readouterr()
#     catalog_json_data = json.loads(out)
# 
#     sys.stdout.write(str(json_data))
# 
#     if any(team['teamTag'] == 'cli-test-team' for team in json_data['teams']):
#         sys.stdout.write("deleting cli-test-team")
#         cli(["teams", "delete", "-t", "cli-test-team"])
# 
#     if any(entity['tag'] == 'cli-test-team' for entity in catalog_json_data['entities']):
#         sys.stdout.write("deleting catalog cli-test-team")
#         cli(["catalog", "delete", "-t", "cli-test-team"])
# 
#     cli(["-d", "teams", "create", "-f", "tests/test_teams.yaml"])

def test_teams_get():
    cli(["teams", "get", "-t", "test-team-1"])

def test_teams_list():
    cli(["teams", "list"])

def test_teams_archive():
    cli(["teams", "archive", "-t", "test-team-1"])
    cli(["teams", "unarchive", "-t", "test-team-1"])

def test_teams_update_metadata():
    cli(["teams", "update-metadata", "-t", "test-team-2", "-f", "tests/test_teams_update.json"])
