from common import *

def test(capsys):
    response = cli_command(capsys, ["catalog", "list", "-g", "public-api-test", "-z", "1"])
    assert (len(response['entities']) == 1)
