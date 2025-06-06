from tests.helpers.utils import *

def test():
    cli(["catalog", "create", "-f", "data/run-time/test-service-metadata.yaml"])

    response = cli(["catalog", "list", "-g", "include-metadata-test"])
    assert (len(response['entities'][0]['metadata']) == 0)

    response = cli(["catalog", "list", "-g", "include-metadata-test", "-m"])
    assert (len(response['entities'][0]['metadata']) > 0)
