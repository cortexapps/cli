from tests.helpers.utils import *

def test():
    response = cli(["catalog", "list", "-g", "cli-test-group-1"])
    assert (response['total'] == 1)
