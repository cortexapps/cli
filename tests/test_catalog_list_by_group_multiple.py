from tests.helpers.utils import *

def test():
    response = cli(["catalog", "list", "-g", "cli-test-group-1,cli-test-group-2"])
    assert (response['total'] == 2)
