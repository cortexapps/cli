from tests.helpers.utils import *

def test():
    response = cli(["catalog", "list", "-o", "payments-team,search-experience"])
    assert (response['total'] == 2)
