from tests.helpers.utils import *

def test():
    cli(["catalog", "create", "-f", "data/run-time/test-service.yaml"])

    response = cli(["catalog", "descriptor", "-y", "-t", "test-service"], ReturnType.STDOUT)
    assert yaml.safe_load(response)['info']['x-cortex-tag'] == "test-service"
