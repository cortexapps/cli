from tests.helpers.utils import *

def test():
    response = cli(["catalog", "descriptor", "-y", "-t", "cli-test-service"], ReturnType.STDOUT)
    assert yaml.safe_load(response)['info']['x-cortex-tag'] == "cli-test-service"
