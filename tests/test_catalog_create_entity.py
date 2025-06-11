from tests.helpers.utils import *

def test():
    cli(["catalog", "create", "-f", "data/import/catalog/cli-test-service.yaml"])

    response = cli(["catalog", "descriptor", "-t", "cli-test-service"])
    assert response['info']['x-cortex-tag'] == "cli-test-service"
