from common import *

def test(capsys):
    response = cli_command(capsys, ["catalog", "list-descriptors", "-t", "component", "-z", "1"])
    assert (len(response['descriptors']) == 1)
