from common import *

def test(capsys):
    response = cli_command(capsys, ["catalog", "list", "-g", "public-api-test-group-1"])
    assert (response['total'] == 1)
