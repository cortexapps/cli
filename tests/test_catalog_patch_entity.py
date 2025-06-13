from tests.helpers.utils import *

def test(capsys):
    cli(["catalog", "patch", "-a", "-f", "data/run-time/patch-entity.yaml"])

    response = cli(["custom-data", "get", "-t", "cli-test-patch-entity", "-k", "owners"])
    assert 'owner-2' in response['value'], "owner-2 should have been merged in owners array"
