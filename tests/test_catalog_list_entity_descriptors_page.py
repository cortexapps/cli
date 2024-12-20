from tests.helpers.utils import *

def test():
    response = cli(["catalog", "list-descriptors", "-t", "component", "-p", "0", "-z", "1"])
    assert response['descriptors'][0]['info']['x-cortex-tag'] == "backend-worker"
