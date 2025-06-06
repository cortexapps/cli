from tests.helpers.utils import *

def test():
    cli(["catalog", "create", "-f", "data/run-time/test-domain-parent.yaml"])
    cli(["catalog", "create", "-f", "data/run-time/test-domain-child.yaml"])
    cli(["catalog", "create", "-f", "data/run-time/test-service.yaml"])
    response = cli(["catalog", "details", "-i", "groups", "-t", "test-service"])
    assert response['hierarchy']['parents'][0]['groups'][0] == 'cli-test', "Entity groups should be in response"
    assert response['hierarchy']['parents'][0]['parents'][0]['groups'][0] == 'cli-test', "Parent groups should be in response"
