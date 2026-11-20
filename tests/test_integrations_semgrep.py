from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_semgrep_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_semgrep_add():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/semgrep/configuration", json={}, status=200)
    cli(["integrations", "semgrep", "add", "-a", "myAlias", "--api-key", "123456", "-oi", "org123", "-os", "my-org", "-i"])

@responses.activate
def test_integrations_semgrep_add_multiple(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/semgrep/configurations", json={}, status=200)
    cli(["integrations", "semgrep", "add-multiple", "-f", str(f)])

@responses.activate
def test_integrations_semgrep_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/semgrep/configuration/test", status=200)
    cli(["integrations", "semgrep", "delete", "-a", "test"])

@responses.activate
def test_integrations_semgrep_delete_all():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/semgrep/configurations", status=200)
    cli(["integrations", "semgrep", "delete-all"])

@responses.activate
def test_integrations_semgrep_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/semgrep/configuration/test", json={}, status=200)
    cli(["integrations", "semgrep", "get", "-a", "test"])

@responses.activate
def test_integrations_semgrep_list():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/semgrep/configurations", json={}, status=200)
    cli(["integrations", "semgrep", "list"])

@responses.activate
def test_integrations_semgrep_get_default():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/semgrep/default-configuration", json={}, status=200)
    cli(["integrations", "semgrep", "get-default"])

@responses.activate
def test_integrations_semgrep_update():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/semgrep/configuration/test", json={}, status=200)
    cli(["integrations", "semgrep", "update", "-a", "test", "-i"])

@responses.activate
def test_integrations_semgrep_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/semgrep/configuration/validate/test", json={}, status=200)
    cli(["integrations", "semgrep", "validate", "-a", "test"])

@responses.activate
def test_integrations_semgrep_validate_all():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/semgrep/configuration/validate", json={}, status=200)
    cli(["integrations", "semgrep", "validate-all"])

@responses.activate
def test_integrations_semgrep_add_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "semgrep", "add", "-a", "test", "--api-key", "key", "-f", str(f)], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_semgrep_add_multiple_valid(tmp_path):
    f = tmp_path / "valid.json"
    f.write_text('{"configurations": []}')
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/semgrep/configurations", json={}, status=200)
    cli(["integrations", "semgrep", "add-multiple", "-f", str(f)])
