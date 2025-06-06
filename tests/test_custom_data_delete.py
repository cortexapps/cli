from tests.helpers.utils import *

def test():
    cli(["catalog", "create", "-f", "data/run-time/test-service.yaml"])

    cli(["custom-data", "add", "-t", "test-service", "-f", "data/run-time/custom-data-delete.json"])

    result = cli(["custom-data", "get", "-t", "test-service", "-k", "delete-me"])
    assert result['value'] == "yes"

    cli(["custom-data", "delete", "-t", "test-service", "-k", "delete-me"])

    result = cli(["catalog", "details", "-t", "test-service"])
    assert not any(metadata['key'] == 'delete-me' for metadata in result['metadata'])
