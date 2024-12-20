from tests.helpers.utils import *

def test():
    response = cli(["catalog", "list", "-g", "public-api-test-group-1,public-api-test-group-2"])
    assert (response['total'] == 2)
