from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_apiiro_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_apiiro_add():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/apiiro/configuration", json={}, status=200)
    cli(["integrations", "apiiro", "add", "-a", "myAlias", "--api-key", "123456", "-i"])

@responses.activate
def test_integrations_apiiro_add_multiple(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/apiiro/configurations", json={}, status=200)
    cli(["integrations", "apiiro", "add-multiple", "-f", str(f)])

@responses.activate
def test_integrations_apiiro_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/apiiro/configuration/test", status=200)
    cli(["integrations", "apiiro", "delete", "-a", "test"])

@responses.activate
def test_integrations_apiiro_delete_all():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/apiiro/configurations", status=200)
    cli(["integrations", "apiiro", "delete-all"])

@responses.activate
def test_integrations_apiiro_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/apiiro/configuration/test", json={}, status=200)
    cli(["integrations", "apiiro", "get", "-a", "test"])

@responses.activate
def test_integrations_apiiro_list():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/apiiro/configurations", json={}, status=200)
    cli(["integrations", "apiiro", "list"])

@responses.activate
def test_integrations_apiiro_get_default():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/apiiro/default-configuration", json={}, status=200)
    cli(["integrations", "apiiro", "get-default"])

@responses.activate
def test_integrations_apiiro_update():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/apiiro/configuration/test", json={}, status=200)
    cli(["integrations", "apiiro", "update", "-a", "test", "-i"])

@responses.activate
def test_integrations_apiiro_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/apiiro/configuration/validate/test", json={}, status=200)
    cli(["integrations", "apiiro", "validate", "-a", "test"])

@responses.activate
def test_integrations_apiiro_validate_all():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/apiiro/configuration/validate", json={}, status=200)
    cli(["integrations", "apiiro", "validate-all"])

@responses.activate
def test_integrations_apiiro_add_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "apiiro", "add", "-a", "test", "--api-key", "key", "-f", str(f)], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_apiiro_add_multiple_valid(tmp_path):
    f = tmp_path / "valid.json"
    f.write_text('{"configurations": []}')
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/apiiro/configurations", json={}, status=200)
    cli(["integrations", "apiiro", "add-multiple", "-f", str(f)])
