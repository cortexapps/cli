from common import *

def test(capsys):
    cli(["-q", "custom-data", "bulk", "-f", "data/run-time/custom-data-bulk.json"])
    capsys.readouterr()

    response = cli_command(capsys, ["catalog", "details", "-t", "backend-worker"])
    list = [metadata for metadata in response['metadata'] if metadata['key'] == "bulk-key-1"]
    assert list[0]['value'] == "value-1"

    response = cli_command(capsys, ["catalog", "details", "-t", "ach-payments-nacha"])
    list = [metadata for metadata in response['metadata'] if metadata['key'] == "bulk-key-4"]
    assert list[0]['value'] == "value-4"
