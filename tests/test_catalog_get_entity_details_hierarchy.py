from tests.helpers.utils import *

def test():
    response = cli(["catalog", "details", "-i", "groups", "-t", "cli-test-service"])
    assert response['hierarchy']['parents'][0]['groups'][0] == 'cli-test', "Entity groups should be in response"
    assert response['hierarchy']['parents'][0]['parents'][0]['groups'][0] == 'cli-test', "Parent groups should be in response"
