from tests.helpers.utils import *

def test():
    cli(["catalog", "create", "-f", "data/run-time/test-service.yaml"])

    result = cli(["catalog", "details", "-t", "test-service"])
    list = [metadata for metadata in result['metadata'] if metadata['key'] == "cicd"]
    assert list[0]['value'] == "circle-ci"
