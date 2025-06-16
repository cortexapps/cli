from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_github_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_github_add():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/github/configuration", json={}, status=200)
    cli(["integrations", "github", "add", "-a", "myAlias", "-h", "my.host.com", "--api-key", "123456", "-i"])

@responses.activate
def test_integrations_github_add_multiple(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/github/configurations", json={}, status=200)
    cli(["integrations", "github", "add-multiple", "-f", str(f)])

@responses.activate
def test_integrations_github_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/github/configuration/test", status=200)
    cli(["integrations", "github", "delete", "-a", "test"])

@responses.activate
def test_integrations_github_delete_all():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/github/configurations", status=200)
    cli(["integrations", "github", "delete-all"])

@responses.activate
def test_integrations_github_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/github/configuration/test", json={}, status=200)
    cli(["integrations", "github", "get", "-a", "test"])

@responses.activate
def test_integrations_github_list():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/github/configurations", json={}, status=200)
    cli(["integrations", "github", "list"])

@responses.activate
def test_integrations_github_get_default():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/github/default-configuration", json={}, status=200)
    cli(["integrations", "github", "get-default"])

@responses.activate
def test_integrations_github_update():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/github/configuration/test", json={}, status=200)
    cli(["integrations", "github", "update", "-a", "test", "-i"])

@responses.activate
def test_integrations_github_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/github/configuration/validate/test", json={}, status=200)
    cli(["integrations", "github", "validate", "-a", "test"])

@responses.activate
def test_integrations_github_validate_all():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/github/configuration/validate", json={}, status=200)
    cli(["integrations", "github", "validate-all"])

@responses.activate
def test_integrations_github_add_personal():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/github/configurations/personal", json={}, status=200)
    cli(["integrations", "github", "add-personal", "-a", "myAlias", "-h", "my.host.com", "--access-token", "123456", "-i"])

@responses.activate
def test_integrations_github_update_personal():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/github/configurations/personal/test", json={}, status=200)
    cli(["integrations", "github", "update-personal", "-a", "test", "-i"])

@responses.activate
def test_integrations_github_delete_personal():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/github/configurations/personal/test", status=200)
    cli(["integrations", "github", "delete-personal", "-a", "test"])
