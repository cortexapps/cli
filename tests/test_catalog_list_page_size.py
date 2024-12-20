from tests.helpers.utils import *

def test():
    response = cli(["catalog", "list", "-g", "public-api-test", "-p", "0", "-z", "1"])
    assert (len(response['entities']) == 1)
