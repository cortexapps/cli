from tests.helpers.utils import *

def test(capsys):
    cli(["catalog", "create", "-f", "data/run-time/test-service.yaml"])

    response = cli(["catalog", "list", "-g", "cli-test", "-io"])
    assert not(response['entities'][0]['owners']['teams'] is None), "Teams array should be returned in result"
