from tests.helpers.utils import *

def test():
    response = cli(["catalog", "create", "-f", "data/run-time/test-service-links.yaml"])

    response = cli(["catalog", "list", "-g", "include-links-test"])
    assert (len(response['entities'][0]['links']) == 0)
    response = cli(["catalog", "list", "-g", "include-links-test", "-l"])
    assert (len(response['entities'][0]['links']) > 0)
