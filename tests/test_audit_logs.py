from common import *

def test(capsys):
    response = cli_command(capsys, ["audit-logs", "get",])
    assert (len(response['logs']) > 0)
