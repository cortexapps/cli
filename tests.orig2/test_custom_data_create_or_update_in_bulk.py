from tests.helpers.utils import *

def test():
    cli(["custom-data", "bulk", "-f", "data/run-time/custom-data-bulk.json"])

    response = json_response(["catalog", "details", "-t", "backend-worker"])
    list = [metadata for metadata in response['metadata'] if metadata['key'] == "bulk-key-1"]
    assert list[0]['value'] == "value-1"

    response = json_response( ["catalog", "details", "-t", "ach-payments-nacha"])
    list = [metadata for metadata in response['metadata'] if metadata['key'] == "bulk-key-4"]
    assert list[0]['value'] == "value-4"
