from tests.helpers.utils import *

def test():
    response = cli(["catalog", "details", "-i", "groups", "-t", "sso-integration"])
    assert response['hierarchy']['parents'][0]['groups'][0] == 'public-api-test', "Entity groups should be in response"
    assert response['hierarchy']['parents'][0]['parents'][0]['groups'][0] == 'public-api-test', "Parent groups should be in response"
