from tests.helpers.utils import *

def test():
    response = cli(["catalog", "list", "-g", "cli-test", "-p", "0", "-z", "1"])
    assert (len(response['entities']) == 1)
