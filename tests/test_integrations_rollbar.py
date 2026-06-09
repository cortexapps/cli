from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_rollbar_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_rollbar_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/rollbar/configuration", json={}, status=200)
    cli(["integrations", "rollbar", "add", "-f", str(f)])

@responses.activate
def test_integrations_rollbar_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/rollbar/default-configuration", json={}, status=200)
    cli(["integrations", "rollbar", "get"])

@responses.activate
def test_integrations_rollbar_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/rollbar/configuration", json={}, status=200)
    cli(["integrations", "rollbar", "update", "-f", str(f)])

@responses.activate
def test_integrations_rollbar_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/rollbar/configuration/validate", json={}, status=200)
    cli(["integrations", "rollbar", "validate"])

@responses.activate
def test_integrations_rollbar_add_with_flags():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/rollbar/configuration", json={}, status=200)
    cli(["integrations", "rollbar", "add", "--access-token", "foo", "--organization-slug", "bar"])

@responses.activate
def test_integrations_rollbar_add_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "rollbar", "add", "-f", str(f), "--access-token", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_rollbar_update_with_flags():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/rollbar/configuration", json={}, status=200)
    cli(["integrations", "rollbar", "update", "--access-token", "foo"])

@responses.activate
def test_integrations_rollbar_update_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "rollbar", "update", "-f", str(f), "--access-token", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_rollbar_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/rollbar/configurations", json={}, status=200)
    cli(["integrations", "rollbar", "delete"])
