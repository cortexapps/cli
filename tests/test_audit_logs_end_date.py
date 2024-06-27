from common import *

def test(capsys):
    end_date = today()
    response = cli_command(capsys, ["audit-logs", "get", "-e", end_date])
    assert (len(response['logs']) > 0)
