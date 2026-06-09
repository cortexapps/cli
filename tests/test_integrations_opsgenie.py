from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_opsgenie_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_opsgenie_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/opsgenie/configuration", json={}, status=200)
    cli(["integrations", "opsgenie", "add", "-f", str(f)])

@responses.activate
def test_integrations_opsgenie_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/opsgenie/default-configuration", json={}, status=200)
    cli(["integrations", "opsgenie", "get"])

@responses.activate
def test_integrations_opsgenie_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/opsgenie/configuration", json={}, status=200)
    cli(["integrations", "opsgenie", "update", "-f", str(f)])

@responses.activate
def test_integrations_opsgenie_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/opsgenie/configuration/validate", json={}, status=200)
    cli(["integrations", "opsgenie", "validate"])

@responses.activate
def test_integrations_opsgenie_add_with_flags():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/opsgenie/configuration", json={}, status=200)
    cli(["integrations", "opsgenie", "add", "--api-token", "foo", "--subdomain", "bar"])

@responses.activate
def test_integrations_opsgenie_add_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "opsgenie", "add", "-f", str(f), "--api-token", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_opsgenie_update_with_flags():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/opsgenie/configuration", json={}, status=200)
    cli(["integrations", "opsgenie", "update", "--api-token", "foo"])

@responses.activate
def test_integrations_opsgenie_update_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "opsgenie", "update", "-f", str(f), "--api-token", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_opsgenie_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/opsgenie/configurations", json={}, status=200)
    cli(["integrations", "opsgenie", "delete"])
