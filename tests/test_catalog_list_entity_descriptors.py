from tests.helpers.utils import *

def test():
    response = cli(["catalog", "list-descriptors", "-t", "api"])
    list = [descriptor for descriptor in response['descriptors'] if descriptor['info']['x-cortex-tag'] == "api-australia"]
    assert list[0]['info']['x-cortex-groups'][0] == "public-api-test"
