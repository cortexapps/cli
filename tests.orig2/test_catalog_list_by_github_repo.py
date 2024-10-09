from common import *

def test(capsys):
    response = cli_command(capsys, ["catalog", "list", "-r", "my-org/my-repo"])
    assert (response['total'] == 1)
