from common import *

def test(capsys):
    response = cli_command(capsys, ["catalog", "list", "-o", "payments-team,search-experience"])
    assert (response['total'] == 2)
