from tests.helpers.utils import *

def test():
    cli(["custom-data", "bulk", "-f", "data/run-time/custom-data-bulk.json"])

    result = cli(["catalog", "details", "-t", "test-service-caller"])
    list = [metadata for metadata in result['metadata'] if metadata['key'] == "bulk-key-1"]
    assert list[0]['value'] == "value-1"

    result = cli( ["catalog", "details", "-t", "test-service-callee"])
    list = [metadata for metadata in result['metadata'] if metadata['key'] == "bulk-key-4"]
    assert list[0]['value'] == "value-4"
