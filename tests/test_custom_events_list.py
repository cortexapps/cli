from tests.helpers.utils import *

def test():

    cli(["catalog", "create", "-f", "data/run-time/test-service.yaml"])
    cli(["custom-events", "delete-all", "-t", "test-service", "-y", "VALIDATE_SERVICE"])
    cli(["custom-events", "create", "-t", "test-service", "-f", "data/run-time/custom-events.json"])

    result = cli(["custom-events", "list", "-t", "test-service"])
    assert result['events'][0]['type'] == "VALIDATE_SERVICE"

    result = cli(["custom-events", "list", "-t", "test-service", "-y", "VALIDATE_SERVICE"])
    assert result['events'][0]['type'] == "VALIDATE_SERVICE"

    result = cli(["custom-events", "list", "-t", "test-service", "-y", "VALIDATE_SERVICE", "-ts", "2023-10-10T13:27:51"])
    assert result['events'][0]['type'] == "VALIDATE_SERVICE"
