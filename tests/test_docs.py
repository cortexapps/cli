from tests.helpers.utils import *

def test_docs():
    cli(["docs", "update", "-t", "cli-test-service", "-f", "data/run-time/docs.yaml"])

    response = cli(["docs", "get", "-t", "cli-test-service"])
    spec = json.loads(response['spec'])
    assert spec['info']['title'] == "Simple API overview", "Returned spec should have a title named 'Simple API overview'"

    cli(["docs", "delete", "-t", "cli-test-service"])

    result = cli(["docs", "get", "-t", "cli-test-service"], ReturnType.RAW)
    out = result.stdout
    assert "HTTP Error 404: Not Found" in out, "An HTTP 404 error code should be thrown"
    assert result.exit_code == 1
