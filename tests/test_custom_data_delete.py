from common import *

def test(capsys):
    cli_command(capsys, ["custom-data", "add", "-t", "recommendations", "-f", "data/run-time/custom-data-delete.json"])

    response = cli_command(capsys, ["custom-data", "get", "-t", "recommendations", "-k", "delete-me"])
    assert response['value'] == "yes"

    cli(["-q", "custom-data", "delete", "-t", "recommendations", "-k", "delete-me"])

    response = cli_command(capsys, ["catalog", "details", "-t", "recommendations"])
    assert not any(metadata['key'] == 'delete-me' for metadata in response['metadata'])
