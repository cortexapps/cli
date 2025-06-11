from tests.helpers.utils import *

def test():
    response = cli(["catalog", "list-descriptors", "-y", "--types", "service"])
    list = [descriptor for descriptor in response['descriptors'] if descriptor['info']['x-cortex-tag'] == "cli-test-service"]
    assert list[0]['info']['x-cortex-custom-metadata']['cicd'] == "circle-ci"
