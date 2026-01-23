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
    cli(["integrations", "newrelic", "add", "-a", "myAlias", "--account-id", "12345", "--personal-key", "NRAK-123456", "-i"])

@responses.activate
def test_integrations_newrelic_add_with_region():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/newrelic/configuration", json={}, status=200)
    cli(["integrations", "newrelic", "add", "-a", "myAlias", "-acc", "12345", "-pk", "NRAK-123456", "-r", "EU"])

def test_integrations_newrelic_add_invalid_key():
    result = cli(["integrations", "newrelic", "add", "-a", "myAlias", "--account-id", "12345", "--personal-key", "invalid-key"], return_type=ReturnType.RAW)
    assert result.exit_code != 0
    assert "must start with 'NRAK'" in result.output

def test_integrations_newrelic_add_missing_required():
    result = cli(["integrations", "newrelic", "add", "-a", "myAlias"], return_type=ReturnType.RAW)
    assert result.exit_code != 0
    assert "are required" in result.output

@responses.activate
def test_integrations_newrelic_add_with_file(tmp_path):
    f = tmp_path / "test_integrations_newrelic_add.json"
    f.write_text('{"alias": "test", "accountId": "12345", "personalKey": "NRAK-123", "region": "US"}')
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/newrelic/configuration", json={}, status=200)
    cli(["integrations", "newrelic", "add", "-f", str(f)])

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
def test_integrations_newrelic_list():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/newrelic/configurations", json={}, status=200)
    cli(["integrations", "newrelic", "list"])

@responses.activate
def test_integrations_newrelic_list_table():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/newrelic/configurations", json={"configurations": [{"alias": "test", "accountId": "123", "region": "US", "isDefault": True}]}, status=200)
    result = cli(["integrations", "newrelic", "list", "--table"], return_type=ReturnType.RAW)
    assert "Alias" in result.output
    assert "test" in result.output

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
