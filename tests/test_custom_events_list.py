from tests.helpers.utils import *

def test():
    cli(["custom-events", "delete-all", "-t", "transaction-store", "-y", "VALIDATE_SERVICE"])
    cli(["custom-events", "create", "-t", "transaction-store", "-f", "data/run-time/custom-events.json"])

    result = cli(["custom-events", "list", "-t", "transaction-store"])
    assert result['events'][0]['type'] == "VALIDATE_SERVICE"

    result = cli(["custom-events", "list", "-t", "transaction-store", "-y", "VALIDATE_SERVICE"])
    assert result['events'][0]['type'] == "VALIDATE_SERVICE"

    result = cli(["custom-events", "list", "-t", "transaction-store", "-y", "VALIDATE_SERVICE", "-ts", "2023-10-10T13:27:51"])
    assert result['events'][0]['type'] == "VALIDATE_SERVICE"
