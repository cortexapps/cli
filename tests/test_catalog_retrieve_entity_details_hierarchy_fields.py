from tests.helpers.utils import *

def test():
    response = cli(["catalog", "details", "-t", "backend-worker", "-i", "groups"])
    assert response['tag'] == "backend-worker"
