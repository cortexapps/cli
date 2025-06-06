from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_datadog_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_datadog_add():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/datadog/configuration", json={}, status=200)
    cli(["integrations", "datadog", "add", "-a", "myAlias", "-r", "US1", "--api-key", "123456", "-i"])

@responses.activate
def test_integrations_datadog_add_multiple(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/datadog/configurations", json={}, status=200)
    cli(["integrations", "datadog", "add-multiple", "-f", str(f)])

@responses.activate
def test_integrations_datadog_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/datadog/configuration/test", status=200)
    cli(["integrations", "datadog", "delete", "-a", "test"])

@responses.activate
def test_integrations_datadog_delete_all():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/datadog/configurations", status=200)
    cli(["integrations", "datadog", "delete-all"])

@responses.activate
def test_integrations_datadog_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/datadog/configuration/test", json={}, status=200)
    cli(["integrations", "datadog", "get", "-a", "test"])

@responses.activate
def test_integrations_datadog_list():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/datadog/configurations", json={}, status=200)
    cli(["integrations", "datadog", "list"])

@responses.activate
def test_integrations_datadog_get_default():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/datadog/default-configuration", json={}, status=200)
    cli(["integrations", "datadog", "get-default"])

@responses.activate
def test_integrations_datadog_update():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/datadog/configuration/test", json={}, status=200)
    cli(["integrations", "datadog", "update", "-a", "test", "-i"])

@responses.activate
def test_integrations_datadog_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/datadog/configuration/validate/test", json={}, status=200)
    cli(["integrations", "datadog", "validate", "-a", "test"])

@responses.activate
def test_integrations_datadog_validate_all():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/datadog/configuration/validate", json={}, status=200)
    cli(["integrations", "datadog", "validate-all"])
