from tests.helpers.utils import *

def test():
    response = cli(["catalog", "descriptor", "-t", "cli-test-service"])
    assert response['info']['x-cortex-tag'] == "cli-test-service"
