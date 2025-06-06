from tests.helpers.utils import *

def test():
    cli(["catalog", "create", "-f", "data/run-time/test-service.yaml"])

    response = cli(["catalog", "list-descriptors", "-t", "service", "-p", "0", "-z", "1"])
    assert (len(response['descriptors']) == 1)
