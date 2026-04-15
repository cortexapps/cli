from tests.helpers.utils import *

def test():
    response = cli(["catalog", "list", "-o", "cli-test-team-1"])
    assert (response['total'] == 1)
