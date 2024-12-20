from tests.helpers.utils import *

def test():
    response = cli(["catalog", "descriptor", "-y", "-t", "backend-worker"], ReturnType.STDOUT)
    assert yaml.safe_load(response)['info']['x-cortex-tag'] == "backend-worker"
