from common import *

def test(capsys):
    response = cli_command(capsys, ["catalog", "details", "-t", "backend-worker"])
    assert response['tag'] == 'backend-worker', "Entity details should be returned"
