from tests.helpers.utils import *

def test(capsys):
    response = cli(["catalog", "list", "-g", "cli-test", "-p", "0"])
    assert (len(response['entities']) > 0)
