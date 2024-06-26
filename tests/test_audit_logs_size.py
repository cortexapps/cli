from common import *

def test(capsys):
    response = cli_command(capsys, ["audit-logs", "get", "-z", "1"])
    assert (len(response['logs']) == 1)
