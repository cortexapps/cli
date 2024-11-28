from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_gitlab_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_gitlab_add():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/gitlab/configuration", json={}, status=200)
    cli(["integrations", "gitlab", "add", "-a", "myAlias", "-h", "my.host.com", "--api-key", "123456", "-i"])

@responses.activate
def test_integrations_gitlab_add_multiple(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/gitlab/configurations", json={}, status=200)
    cli(["integrations", "gitlab", "add-multiple", "-f", str(f)])

@responses.activate
def test_integrations_gitlab_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/gitlab/configuration/test", status=200)
    cli(["integrations", "gitlab", "delete", "-a", "test"])

@responses.activate
def test_integrations_gitlab_delete_all():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/gitlab/configurations", status=200)
    cli(["integrations", "gitlab", "delete-all"])

@responses.activate
def test_integrations_gitlab_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/gitlab/configuration/test", json={}, status=200)
    cli(["integrations", "gitlab", "get", "-a", "test"])

@responses.activate
def test_integrations_gitlab_get_all():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/gitlab/configurations", json={}, status=200)
    cli(["integrations", "gitlab", "get-all"])

@responses.activate
def test_integrations_gitlab_get_default():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/gitlab/default-configuration", json={}, status=200)
    cli(["integrations", "gitlab", "get-default"])

@responses.activate
def test_integrations_gitlab_update():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/gitlab/configuration/test", json={}, status=200)
    cli(["integrations", "gitlab", "update", "-a", "test", "-i"])

@responses.activate
def test_integrations_gitlab_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/gitlab/configuration/validate/test", json={}, status=200)
    cli(["integrations", "gitlab", "validate", "-a", "test"])

@responses.activate
def test_integrations_gitlab_validate_all():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/gitlab/configuration/validate", json={}, status=200)
    cli(["integrations", "gitlab", "validate-all"])
