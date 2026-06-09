from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_servicenow_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_servicenow_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/servicenow/configuration", json={}, status=200)
    cli(["integrations", "servicenow", "add", "-f", str(f)])

@responses.activate
def test_integrations_servicenow_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/servicenow/default-configuration", json={}, status=200)
    cli(["integrations", "servicenow", "get"])

@responses.activate
def test_integrations_servicenow_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/servicenow/configuration", json={}, status=200)
    cli(["integrations", "servicenow", "update", "-f", str(f)])

@responses.activate
def test_integrations_servicenow_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/servicenow/configuration/validate", json={}, status=200)
    cli(["integrations", "servicenow", "validate"])

@responses.activate
def test_integrations_servicenow_add_with_flags():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/servicenow/configuration", json={}, status=200)
    cli(["integrations", "servicenow", "add", "--instance-name", "foo", "--password", "bar", "--username", "baz"])

@responses.activate
def test_integrations_servicenow_add_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "servicenow", "add", "-f", str(f), "--instance-name", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_servicenow_update_with_flags():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/servicenow/configuration", json={}, status=200)
    cli(["integrations", "servicenow", "update", "--instance-name", "foo"])

@responses.activate
def test_integrations_servicenow_update_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "servicenow", "update", "-f", str(f), "--instance-name", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_servicenow_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/servicenow/configurations", json={}, status=200)
    cli(["integrations", "servicenow", "delete"])
