from common import *

@pytest.mark.skip(reason="Disabled until CET-15982 is resolved.")
def test(capsys):
    end_date = today()
    response = cli_command(capsys, ["audit-logs", "get", "-e", end_date])
    assert (len(response['logs']) > 0)
