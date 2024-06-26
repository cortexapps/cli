from common import *

def test(capsys):
    response = cli_command(capsys, ["catalog", "list", "-g", "public-api-test-group-1,public-api-test-group-2"])
    assert (response['total'] == 2)
