from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_argocd_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_argocd_add():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/argocd/configuration", json={}, status=200)
    cli(["integrations", "argocd", "add", "-a", "myAlias", "-h", "https://argocd.example.com", "-p", "pass123", "-u", "admin", "-i"])

@responses.activate
def test_integrations_argocd_add_multiple(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/argocd/configurations", json={}, status=200)
    cli(["integrations", "argocd", "add-multiple", "-f", str(f)])

@responses.activate
def test_integrations_argocd_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/argocd/configuration/test", status=200)
    cli(["integrations", "argocd", "delete", "-a", "test"])

@responses.activate
def test_integrations_argocd_delete_all():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/argocd/configurations", status=200)
    cli(["integrations", "argocd", "delete-all"])

@responses.activate
def test_integrations_argocd_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/argocd/configuration/test", json={}, status=200)
    cli(["integrations", "argocd", "get", "-a", "test"])

@responses.activate
def test_integrations_argocd_list():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/argocd/configurations", json={}, status=200)
    cli(["integrations", "argocd", "list"])

@responses.activate
def test_integrations_argocd_get_default():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/argocd/default-configuration", json={}, status=200)
    cli(["integrations", "argocd", "get-default"])

@responses.activate
def test_integrations_argocd_update():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/argocd/configuration/test", json={}, status=200)
    cli(["integrations", "argocd", "update", "-a", "test", "-i"])

@responses.activate
def test_integrations_argocd_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/argocd/configuration/validate/test", json={}, status=200)
    cli(["integrations", "argocd", "validate", "-a", "test"])

@responses.activate
def test_integrations_argocd_validate_all():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/argocd/configuration/validate", json={}, status=200)
    cli(["integrations", "argocd", "validate-all"])

@responses.activate
def test_integrations_argocd_add_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "argocd", "add", "-a", "test", "-h", "host", "-u", "user", "-p", "pass", "-f", str(f)], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_argocd_add_multiple_valid(tmp_path):
    f = tmp_path / "valid.json"
    f.write_text('{"configurations": []}')
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/argocd/configurations", json={}, status=200)
    cli(["integrations", "argocd", "add-multiple", "-f", str(f)])
