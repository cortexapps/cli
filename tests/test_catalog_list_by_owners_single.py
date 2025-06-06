from tests.helpers.utils import *

def test():
    cli(["catalog", "create", "-f", "data/run-time/test-team-1.yaml"])
    cli(["catalog", "create", "-f", "data/run-time/test-service-test-team-1.yaml"])

    response = cli(["catalog", "list", "-o", "test-team-1"])
    assert (response['total'] == 1)
