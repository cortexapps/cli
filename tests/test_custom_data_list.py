from tests.helpers.utils import *

def test():
    result = cli(["catalog", "details", "-t", "cli-test-service"])
    list = [metadata for metadata in result['metadata'] if metadata['key'] == "cicd"]
    assert list[0]['value'] == "circle-ci"
