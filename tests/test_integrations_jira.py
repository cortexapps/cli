from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_jira_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_jira_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/jira/configuration", json={}, status=200)
    cli(["integrations", "jira", "add", "-f", str(f)])

@responses.activate
def test_integrations_jira_add_multiple(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/jira/configurations", json={}, status=200)
    cli(["integrations", "jira", "add-multiple", "-f", str(f)])

@responses.activate
def test_integrations_jira_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/jira/configuration/test", status=200)
    cli(["integrations", "jira", "delete", "-a", "test"])

@responses.activate
def test_integrations_jira_delete_all():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/jira/configurations", status=200)
    cli(["integrations", "jira", "delete-all"])

@responses.activate
def test_integrations_jira_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/jira/configuration/test", json={}, status=200)
    cli(["integrations", "jira", "get", "-a", "test"])

@responses.activate
def test_integrations_jira_list():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/jira/configurations", json={}, status=200)
    cli(["integrations", "jira", "list"])

@responses.activate
def test_integrations_jira_get_default():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/jira/default-configuration", json={}, status=200)
    cli(["integrations", "jira", "get-default"])

@responses.activate
def test_integrations_jira_update():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/jira/configuration/test", json={}, status=200)
    cli(["integrations", "jira", "update", "-a", "test", "-i"])

@responses.activate
def test_integrations_jira_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/jira/configuration/validate/test", json={}, status=200)
    cli(["integrations", "jira", "validate", "-a", "test"])

@responses.activate
def test_integrations_jira_validate_all():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/jira/configuration/validate", json={}, status=200)
    cli(["integrations", "jira", "validate-all"])

@responses.activate
def test_integrations_jira_add_valid(tmp_path):
    f = tmp_path / "valid.json"
    f.write_text('{"alias": "test", "email": "test@test.com", "host": "jira.test.com", "apiToken": "token"}')
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/jira/configuration", json={}, status=200)
    cli(["integrations", "jira", "add", "-f", str(f)])

@responses.activate
def test_integrations_jira_add_multiple_valid(tmp_path):
    f = tmp_path / "valid.json"
    f.write_text('{"configurations": []}')
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/jira/configurations", json={}, status=200)
    cli(["integrations", "jira", "add-multiple", "-f", str(f)])
