from common import *

def test(capsys):
    response = cli_command(capsys, ["catalog", "descriptor", "-y", "-t", "backend-worker"], "text")
    assert yaml.safe_load(response)['info']['x-cortex-tag'] == "backend-worker"
