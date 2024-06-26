from common import *

def test(capsys):
    response = cli_command(capsys, ["catalog", "descriptor", "-t", "backend-worker"])
    assert response['info']['x-cortex-tag'] == "backend-worker"
