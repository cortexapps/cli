from common import *

def test(capsys):
    cli(["-q", "custom-events", "delete-all", "-t", "transaction-store", "-y", "VALIDATE_SERVICE"])
    cli(["-q", "custom-events", "create", "-t", "transaction-store", "-f", "data/run-time/custom-events.json"])
    capsys.readouterr()

    response = cli_command(capsys, ["custom-events", "list", "-t", "transaction-store"])
    assert response['events'][0]['type'] == "VALIDATE_SERVICE"

    response = cli_command(capsys, ["custom-events", "list", "-t", "transaction-store", "-y", "VALIDATE_SERVICE"])
    assert response['events'][0]['type'] == "VALIDATE_SERVICE"

    response = cli_command(capsys, ["custom-events", "list", "-t", "transaction-store", "-y", "VALIDATE_SERVICE", "-i", "2023-10-10T13:27:51.226"])
    assert response['events'][0]['type'] == "VALIDATE_SERVICE"
