from tests.helpers.utils import *

def test():
    response = cli( ["catalog", "details", "-t", "cli-test-service"])
    assert response['tag'] == 'cli-test-service', "Entity details should be returned"
