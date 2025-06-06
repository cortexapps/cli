from tests.helpers.utils import *

def test(capsys):
    cli(["catalog", "create", "-f", "data/run-time/test-service.yaml"])

    response = cli(["catalog", "list", "-g", "cli-test", "-p", "0"])
    assert (len(response['entities']) > 0)
