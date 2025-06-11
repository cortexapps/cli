from tests.helpers.utils import *

def test():
    response = cli(["catalog", "details", "-t", "cli-test-service", "-i", "groups"])
    assert response['tag'] == "cli-test-service"
