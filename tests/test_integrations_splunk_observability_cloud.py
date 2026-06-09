from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_splunk_observability_cloud_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_splunk_observability_cloud_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/signalfx/configuration", json={}, status=200)
    cli(["integrations", "splunk-observability-cloud", "add", "-f", str(f)])

@responses.activate
def test_integrations_splunk_observability_cloud_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/signalfx/default-configuration", json={}, status=200)
    cli(["integrations", "splunk-observability-cloud", "get"])

@responses.activate
def test_integrations_splunk_observability_cloud_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/signalfx/configuration", json={}, status=200)
    cli(["integrations", "splunk-observability-cloud", "update", "-f", str(f)])

@responses.activate
def test_integrations_splunk_observability_cloud_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/signalfx/configuration/validate", json={}, status=200)
    cli(["integrations", "splunk-observability-cloud", "validate"])

@responses.activate
def test_integrations_splunk_observability_cloud_add_with_flags():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/signalfx/configuration", json={}, status=200)
    cli(["integrations", "splunk-observability-cloud", "add", "--access-token", "foo", "--realm", "bar"])

@responses.activate
def test_integrations_splunk_observability_cloud_add_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "splunk-observability-cloud", "add", "-f", str(f), "--access-token", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_splunk_observability_cloud_update_with_flags():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/signalfx/configuration", json={}, status=200)
    cli(["integrations", "splunk-observability-cloud", "update", "--access-token", "foo"])

@responses.activate
def test_integrations_splunk_observability_cloud_update_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "splunk-observability-cloud", "update", "-f", str(f), "--access-token", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_splunk_observability_cloud_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/signalfx/configurations", json={}, status=200)
    cli(["integrations", "splunk-observability-cloud", "delete"])
