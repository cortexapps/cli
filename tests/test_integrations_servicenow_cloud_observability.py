from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_servicenow_cloud_observability_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_servicenow_cloud_observability_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/lightstep/configuration", json={}, status=200)
    cli(["integrations", "servicenow-cloud-observability", "add", "-f", str(f)])

@responses.activate
def test_integrations_servicenow_cloud_observability_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/lightstep/default-configuration", json={}, status=200)
    cli(["integrations", "servicenow-cloud-observability", "get"])

@responses.activate
def test_integrations_servicenow_cloud_observability_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/lightstep/configuration", json={}, status=200)
    cli(["integrations", "servicenow-cloud-observability", "update", "-f", str(f)])

@responses.activate
def test_integrations_servicenow_cloud_observability_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/lightstep/configuration/validate", json={}, status=200)
    cli(["integrations", "servicenow-cloud-observability", "validate"])

@responses.activate
def test_integrations_servicenow_cloud_observability_add_with_flags():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/lightstep/configuration", json={}, status=200)
    cli(["integrations", "servicenow-cloud-observability", "add", "--auth-token", "foo", "--organization-id", "bar", "--project-id", "baz"])

@responses.activate
def test_integrations_servicenow_cloud_observability_add_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "servicenow-cloud-observability", "add", "-f", str(f), "--auth-token", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_servicenow_cloud_observability_update_with_flags():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/lightstep/configuration", json={}, status=200)
    cli(["integrations", "servicenow-cloud-observability", "update", "--auth-token", "foo"])

@responses.activate
def test_integrations_servicenow_cloud_observability_update_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "servicenow-cloud-observability", "update", "-f", str(f), "--auth-token", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_servicenow_cloud_observability_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/lightstep/configurations", json={}, status=200)
    cli(["integrations", "servicenow-cloud-observability", "delete"])
