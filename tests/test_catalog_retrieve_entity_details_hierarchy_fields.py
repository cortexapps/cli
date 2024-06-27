from common import *

def test(capsys):
    response = cli_command(capsys, ["catalog", "details", "-t", "backend-worker", "-i", "groups"])
    assert response['tag'] == "backend-worker"
