from tests.helpers.utils import *

def test():
    response = cli(["catalog", "list-descriptors", "-y", "--types", "component"])
    list = [descriptor for descriptor in response['descriptors'] if descriptor['info']['x-cortex-tag'] == "backend-worker"]
    print("list = " + str(list))
    assert list[0]['info']['x-cortex-custom-metadata']['cicd'] == "circle-ci"
