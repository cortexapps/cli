from tests.helpers.utils import *

def test():
    response = cli(["catalog", "descriptor", "-t", "backend-worker"])
    print(response)
    assert response['info']['x-cortex-tag'] == "backend-worker"
