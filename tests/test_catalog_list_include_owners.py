from common import *

def test(capsys):
    response = cli_command(capsys, ["catalog", "list", "-g", "public-api-test", "-io"])
    assert not(response['entities'][0]['owners']['teams'] is None), "Teams array should be returned in result"
