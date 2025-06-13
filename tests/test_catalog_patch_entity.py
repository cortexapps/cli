from common import *

def test(capsys):
    cli(["-q", "catalog", "patch", "-f", "data/run-time/create-patch-entity.yaml"])
    # Need to clear captured system output from the above commands to clear the way for the next one.
    capsys.readouterr()

    response = cli_command(capsys, ["catalog", "descriptor", "-t", "patch-entity"])
    assert response['info']['x-cortex-tag'] == "patch-entity"

    # Need to clear captured system output from the above commands to clear the way for the next one.
    capsys.readouterr()

    cli(["-q", "catalog", "patch", "-a", "-f", "data/run-time/patch-entity.yaml"])
    capsys.readouterr()

    response = cli_command(capsys, ["custom-data", "get", "-t", "patch-entity", "-k", "owners"])
    assert 'owner-2' in response['value'], "owner-2 should have been merged in owners array"
