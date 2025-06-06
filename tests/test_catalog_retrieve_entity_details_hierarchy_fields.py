from tests.helpers.utils import *

def test():
    cli(["catalog", "create", "-f", "data/run-time/test-service.yaml"])

    response = cli(["catalog", "details", "-t", "test-service", "-i", "groups"])
    assert response['tag'] == "test-service"
