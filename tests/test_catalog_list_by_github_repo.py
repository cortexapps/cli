from tests.helpers.utils import *

def test():
    response = cli( ["catalog", "list", "-r", "my-org/my-repo"])
    assert (response['total'] == 1)
