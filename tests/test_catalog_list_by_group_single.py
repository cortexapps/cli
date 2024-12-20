from tests.helpers.utils import *

def test():
    response = cli(["catalog", "list", "-g", "public-api-test-group-1"])
    assert (response['total'] == 1)
