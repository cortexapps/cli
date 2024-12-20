from tests.helpers.utils import *

def test():
    response = cli( ["catalog", "details", "-t", "backend-worker"])
    assert response['tag'] == 'backend-worker', "Entity details should be returned"
