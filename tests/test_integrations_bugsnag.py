from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_bugsnag_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_bugsnag_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/bugsnag/configuration", json={}, status=200)
    cli(["integrations", "bugsnag", "add", "-f", str(f)])

@responses.activate
def test_integrations_bugsnag_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/bugsnag/default-configuration", json={}, status=200)
    cli(["integrations", "bugsnag", "get"])

@responses.activate
def test_integrations_bugsnag_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/bugsnag/configuration", json={}, status=200)
    cli(["integrations", "bugsnag", "update", "-f", str(f)])

@responses.activate
def test_integrations_bugsnag_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/bugsnag/configuration/validate", json={}, status=200)
    cli(["integrations", "bugsnag", "validate"])

@responses.activate
def test_integrations_bugsnag_add_with_flags():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/bugsnag/configuration", json={}, status=200)
    cli(["integrations", "bugsnag", "add", "--auth-token", "foo", "--organization-id", "bar"])

@responses.activate
def test_integrations_bugsnag_add_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "bugsnag", "add", "-f", str(f), "--auth-token", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_bugsnag_update_with_flags():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/bugsnag/configuration", json={}, status=200)
    cli(["integrations", "bugsnag", "update", "--auth-token", "foo"])

@responses.activate
def test_integrations_bugsnag_update_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "bugsnag", "update", "-f", str(f), "--auth-token", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_bugsnag_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/bugsnag/configurations", json={}, status=200)
    cli(["integrations", "bugsnag", "delete"])
