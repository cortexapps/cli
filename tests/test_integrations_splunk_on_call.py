from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_splunk_on_call_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_splunk_on_call_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/victorops/configuration", json={}, status=200)
    cli(["integrations", "splunk-on-call", "add", "-f", str(f)])

@responses.activate
def test_integrations_splunk_on_call_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/victorops/default-configuration", json={}, status=200)
    cli(["integrations", "splunk-on-call", "get"])

@responses.activate
def test_integrations_splunk_on_call_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/victorops/configuration", json={}, status=200)
    cli(["integrations", "splunk-on-call", "update", "-f", str(f)])

@responses.activate
def test_integrations_splunk_on_call_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/victorops/configuration/validate", json={}, status=200)
    cli(["integrations", "splunk-on-call", "validate"])

@responses.activate
def test_integrations_splunk_on_call_add_with_flags():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/victorops/configuration", json={}, status=200)
    cli(["integrations", "splunk-on-call", "add", "--api-id", "foo", "--api-key", "bar", "--organization", "baz"])

@responses.activate
def test_integrations_splunk_on_call_add_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "splunk-on-call", "add", "-f", str(f), "--api-id", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_splunk_on_call_update_with_flags():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/victorops/configuration", json={}, status=200)
    cli(["integrations", "splunk-on-call", "update", "--api-id", "foo"])

@responses.activate
def test_integrations_splunk_on_call_update_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "splunk-on-call", "update", "-f", str(f), "--api-id", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_splunk_on_call_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/victorops/configurations", json={}, status=200)
    cli(["integrations", "splunk-on-call", "delete"])
