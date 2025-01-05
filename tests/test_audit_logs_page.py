from common import *

@pytest.mark.skip(reason="Disabled until CET-15982 is resolved.")
def test(capsys):
    response = cli_command(capsys, ["audit-logs", "get", "-p", "0",])
    assert (len(response['logs']) > 0)
