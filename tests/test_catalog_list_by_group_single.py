from tests.helpers.utils import *

def test():
    cli(["catalog", "create", "-f", "data/run-time/test-service-group-1.yaml"])

    response = cli(["catalog", "list", "-g", "cli-test-group-1"])
    assert (response['total'] == 1)
