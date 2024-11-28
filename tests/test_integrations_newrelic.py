from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_newrelic_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_newrelic_add():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/newrelic/configuration", json={}, status=200)
    cli(["integrations", "newrelic", "add", "-a", "myAlias", "-h", "my.host.com", "--api-key", "123456", "-i"])

@responses.activate
def test_integrations_newrelic_add_multiple(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/newrelic/configurations", json={}, status=200)
    cli(["integrations", "newrelic", "add-multiple", "-f", str(f)])

@responses.activate
def test_integrations_newrelic_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/newrelic/configuration/test", status=200)
    cli(["integrations", "newrelic", "delete", "-a", "test"])

@responses.activate
def test_integrations_newrelic_delete_all():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/newrelic/configurations", status=200)
    cli(["integrations", "newrelic", "delete-all"])

@responses.activate
def test_integrations_newrelic_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/newrelic/configuration/test", json={}, status=200)
    cli(["integrations", "newrelic", "get", "-a", "test"])

@responses.activate
def test_integrations_newrelic_get_all():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/newrelic/configurations", json={}, status=200)
    cli(["integrations", "newrelic", "get-all"])

@responses.activate
def test_integrations_newrelic_get_default():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/newrelic/default-configuration", json={}, status=200)
    cli(["integrations", "newrelic", "get-default"])

@responses.activate
def test_integrations_newrelic_update():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/newrelic/configuration/test", json={}, status=200)
    cli(["integrations", "newrelic", "update", "-a", "test", "-i"])

@responses.activate
def test_integrations_newrelic_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/newrelic/configuration/validate/test", json={}, status=200)
    cli(["integrations", "newrelic", "validate", "-a", "test"])

@responses.activate
def test_integrations_newrelic_validate_all():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/newrelic/configuration/validate", json={}, status=200)
    cli(["integrations", "newrelic", "validate-all"])
