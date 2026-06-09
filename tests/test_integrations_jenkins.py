from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_jenkins_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_jenkins_add():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/jenkins/configuration", json={}, status=200)
    cli(["integrations", "jenkins", "add", "-a", "myAlias", "--api-key", "123456", "-h", "https://jenkins.example.com", "-u", "admin", "-i"])

@responses.activate
def test_integrations_jenkins_add_multiple(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/jenkins/configurations", json={}, status=200)
    cli(["integrations", "jenkins", "add-multiple", "-f", str(f)])

@responses.activate
def test_integrations_jenkins_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/jenkins/configuration/test", status=200)
    cli(["integrations", "jenkins", "delete", "-a", "test"])

@responses.activate
def test_integrations_jenkins_delete_all():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/jenkins/configurations", status=200)
    cli(["integrations", "jenkins", "delete-all"])

@responses.activate
def test_integrations_jenkins_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/jenkins/configuration/test", json={}, status=200)
    cli(["integrations", "jenkins", "get", "-a", "test"])

@responses.activate
def test_integrations_jenkins_list():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/jenkins/configurations", json={}, status=200)
    cli(["integrations", "jenkins", "list"])

@responses.activate
def test_integrations_jenkins_get_default():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/jenkins/default-configuration", json={}, status=200)
    cli(["integrations", "jenkins", "get-default"])

@responses.activate
def test_integrations_jenkins_update():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/jenkins/configuration/test", json={}, status=200)
    cli(["integrations", "jenkins", "update", "-a", "test", "-i"])

@responses.activate
def test_integrations_jenkins_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/jenkins/configuration/validate/test", json={}, status=200)
    cli(["integrations", "jenkins", "validate", "-a", "test"])

@responses.activate
def test_integrations_jenkins_validate_all():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/jenkins/configuration/validate", json={}, status=200)
    cli(["integrations", "jenkins", "validate-all"])

@responses.activate
def test_integrations_jenkins_add_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "jenkins", "add", "-a", "test", "--api-key", "key", "-h", "host", "-u", "user", "-f", str(f)], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_jenkins_add_multiple_valid(tmp_path):
    f = tmp_path / "valid.json"
    f.write_text('{"configurations": []}')
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/jenkins/configurations", json={}, status=200)
    cli(["integrations", "jenkins", "add-multiple", "-f", str(f)])
