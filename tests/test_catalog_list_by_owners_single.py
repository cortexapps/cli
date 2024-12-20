from tests.helpers.utils import *

def test():
    response = cli(["catalog", "list", "-o", "payments-team"])
    assert (response['total'] == 1)
