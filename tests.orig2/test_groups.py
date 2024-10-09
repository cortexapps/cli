from common import *

def test(capsys):
    cli_command(capsys, ["catalog", "create", "-f", "data/run-time/groups-entity.yaml"])

    cli_command(capsys, ["groups", "add", "-t", "groups-entity", "-f", "data/run-time/groups.json"])

    response = cli_command(capsys, ["groups", "get", "-t", "groups-entity"])
    assert any(group['tag'] == "group1" for group in response['groups']), "Entity should have 'group1' as a group"

    cli(["-q", "groups", "delete", "-t", "groups-entity", "-f", "data/run-time/groups.json"])

    response = cli_command(capsys, ["groups", "get", "-t", "groups-entity"])
    assert not any(group['tag'] == "group1" for group in response['groups']), "Entity should NOT have 'group1' as a group"
