from common import *

def test(capsys):
    response = cli_command(capsys, ["audit-logs", "get", "-p", "0",])
    assert (len(response['logs']) > 0)
