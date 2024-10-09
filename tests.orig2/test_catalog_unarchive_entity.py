from common import *

def test(capsys):
    cli(["-q", "catalog", "create", "-f", "data/run-time/unarchive-entity.yaml"])
    cli(["-q", "catalog", "archive", "-t", "unarchive-entity"])
    # Need to clear captured system output from the above commands to clear the way for the next one.
    capsys.readouterr()

    response = cli_command(capsys, ["catalog", "details", "-t", "unarchive-entity"])
    assert response['isArchived'] == True, "isArchived attribute should be true"

    response = cli_command(capsys, ["catalog", "unarchive", "-t", "unarchive-entity"])
    assert response['isArchived'] == False, "isArchived attribute should not be true"
