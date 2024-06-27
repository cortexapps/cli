from common import *

def test(capsys):
    cli(["-q", "catalog", "create", "-f", "data/run-time/archive-entity.yaml"])
    cli(["-q", "catalog", "archive", "-t", "archive-entity"])
    # Need to clear captured system output from the above commands to clear the way for the next one.
    capsys.readouterr()

    response = cli_command(capsys, ["catalog", "details", "-t", "archive-entity"])
    assert response['isArchived'] == True, "isArchived attribute should be true"
