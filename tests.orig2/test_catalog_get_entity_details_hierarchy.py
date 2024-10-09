from common import *

def test(capsys):
    response = cli_command(capsys, ["catalog", "details", "-i", "groups", "-t", "sso-integration"])
    assert response['hierarchy']['parents'][0]['groups'][0] == 'public-api-test', "Entity groups should be in response"
    assert response['hierarchy']['parents'][0]['parents'][0]['groups'][0] == 'public-api-test', "Parent groups should be in response"
