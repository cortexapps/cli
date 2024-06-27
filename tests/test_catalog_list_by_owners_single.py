from common import *

def test(capsys):
    response = cli_command(capsys, ["catalog", "list", "-o", "payments-team"])
    assert (response['total'] == 1)
