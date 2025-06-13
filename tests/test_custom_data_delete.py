from tests.helpers.utils import *

def test():
    cli(["custom-data", "add", "-t", "cli-test-service", "-f", "data/run-time/custom-data-delete.json"])

    result = cli(["custom-data", "get", "-t", "cli-test-service", "-k", "delete-me"])
    assert result['value'] == "yes"

    cli(["custom-data", "delete", "-t", "cli-test-service", "-k", "delete-me"])

    result = cli(["catalog", "details", "-t", "cli-test-service"])
    assert not any(metadata['key'] == 'delete-me' for metadata in result['metadata'])
