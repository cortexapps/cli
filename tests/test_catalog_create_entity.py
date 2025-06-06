from tests.helpers.utils import *

def test():
    cli(["catalog", "create", "-f", "data/run-time/test-service.yaml"])

    response = cli(["catalog", "descriptor", "-t", "test-service"])
    assert response['info']['x-cortex-tag'] == "test-service"
