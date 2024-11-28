from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_sonarqube_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_sonarqube_add():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/sonarqube/configuration", json={}, status=200)
    cli(["integrations", "sonarqube", "add", "-a", "myAlias", "-h", "my.host.com", "--api-key", "123456", "-i"])

@responses.activate
def test_integrations_sonarqube_add_multiple(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/sonarqube/configurations", json={}, status=200)
    cli(["integrations", "sonarqube", "add-multiple", "-f", str(f)])

@responses.activate
def test_integrations_sonarqube_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/sonarqube/configuration/test", status=200)
    cli(["integrations", "sonarqube", "delete", "-a", "test"])

@responses.activate
def test_integrations_sonarqube_delete_all():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/sonarqube/configurations", status=200)
    cli(["integrations", "sonarqube", "delete-all"])

@responses.activate
def test_integrations_sonarqube_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/sonarqube/configuration/test", json={}, status=200)
    cli(["integrations", "sonarqube", "get", "-a", "test"])

@responses.activate
def test_integrations_sonarqube_get_all():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/sonarqube/configurations", json={}, status=200)
    cli(["integrations", "sonarqube", "get-all"])

@responses.activate
def test_integrations_sonarqube_get_default():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/sonarqube/default-configuration", json={}, status=200)
    cli(["integrations", "sonarqube", "get-default"])

@responses.activate
def test_integrations_sonarqube_update():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/sonarqube/configuration/test", json={}, status=200)
    cli(["integrations", "sonarqube", "update", "-a", "test", "-i"])

@responses.activate
def test_integrations_sonarqube_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/sonarqube/configuration/validate/test", json={}, status=200)
    cli(["integrations", "sonarqube", "validate", "-a", "test"])

@responses.activate
def test_integrations_sonarqube_validate_all():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/sonarqube/configuration/validate", json={}, status=200)
    cli(["integrations", "sonarqube", "validate-all"])
