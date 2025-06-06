from tests.helpers.utils import *

def test():
    cli(["catalog", "create", "-f", "data/run-time/test-service.yaml"])

    response = cli(["catalog", "list", "-g", "cli-test", "-t", "service"])
    assert response['total'] > 0, "Should find at least 1 entity of type 'service'"
