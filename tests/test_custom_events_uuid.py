from tests.helpers.utils import *

def test():
    result = cli(["catalog", "create", "-f", "data/run-time/test-service.yaml"])

    result = cli(["custom-events", "create", "-t", "test-service", "-f", "data/run-time/custom-events-configure.json"])
    uuid = result['uuid']

    result = cli(["custom-events", "get-by-uuid", "-t", "test-service", "-u", uuid])
    assert result['type'] == "CONFIG_SERVICE"

    cli(["custom-events", "update-by-uuid", "-t", "test-service", "-u", uuid, "-f", "data/run-time/custom-events.json"])

    result = cli(["custom-events", "get-by-uuid", "-t", "test-service", "-u", uuid])
    assert result['type'] == "VALIDATE_SERVICE"

    cli(["custom-events", "delete-by-uuid", "-t", "test-service", "-u", uuid])

    # Custom event was deleted, so verify it cannot be retrieved.
    # with pytest.raises(SystemExit) as excinfo:
    result = cli(["custom-events", "get-by-uuid", "-t", "test-service", "-u", uuid], ReturnType.RAW)
    out = result.stdout
    assert "HTTP Error 404: Not Found" in out, "An HTTP 404 error code should be thrown"
    assert result.exit_code == 1

    cli(["custom-events", "delete-all", "-t", "test-service"])
