from common import *

@pytest.mark.skip(reason="Disabled until CET-15982 is resolved.")
def test(capsys):
    start_date = yesterday()
    end_date = today()
    response = cli_command(capsys, ["audit-logs", "get", "-s", start_date, "-e", end_date])
    assert (len(response['logs']) > 0)
