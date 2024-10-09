from common import *

def test(capsys):
    response = cli_command(capsys, ["teams", "list"])
    assert any(team['teamTag'] == 'payments-team' for team in response['teams'])
