from common import *

def test(capsys):
    cli(["-q", "catalog", "create", "-f", "data/run-time/create-entity.yaml"])
    # Need to clear captured system output from the above commands to clear the way for the next one.
    capsys.readouterr()

    response = cli_command(capsys, ["catalog", "descriptor", "-t", "create-entity"])
    assert response['info']['x-cortex-tag'] == "create-entity"
