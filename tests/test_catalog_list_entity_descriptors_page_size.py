from tests.helpers.utils import *

def test():
    response = cli(["catalog", "list-descriptors", "-t", "component", "-p", "0", "-z", "1"])
    assert (len(response['descriptors']) == 1)
