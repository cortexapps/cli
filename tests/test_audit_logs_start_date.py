from common import *

def test(capsys):
    start_date = yesterday()
    response = cli_command(capsys, ["audit-logs", "get", "-s", start_date])
    assert (len(response['logs']) > 0)
