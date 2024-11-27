from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_circle_ci_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_circle_ci_add():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/circleci/configuration", json={}, status=200)
    cli(["integrations", "circleci", "add", "-a", "myAlias", "-h", "my.host.com", "--api-key", "123456", "-i"])

@responses.activate
def test_integrations_circle_ci_add_multiple(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/circleci/configurations", json={}, status=200)
    cli(["integrations", "circleci", "add-multiple", "-f", str(f)])

@responses.activate
def test_integrations_circle_ci_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/circleci/configuration/test", status=200)
    cli(["integrations", "circleci", "delete", "-a", "test"])

@responses.activate
def test_integrations_circle_ci_delete_all():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/circleci/configurations", status=200)
    cli(["integrations", "circleci", "delete-all"])

@responses.activate
def test_integrations_circle_ci_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/circleci/configuration/test", json={}, status=200)
    cli(["integrations", "circleci", "get", "-a", "test"])

@responses.activate
def test_integrations_circle_ci_get_all():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/circleci/configurations", json={}, status=200)
    cli(["integrations", "circleci", "get-all"])

@responses.activate
def test_integrations_circle_ci_get_default():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/circleci/default-configuration", json={}, status=200)
    cli(["integrations", "circleci", "get-default"])

@responses.activate
def test_integrations_circle_ci_update():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/circleci/configuration/test", json={}, status=200)
    cli(["integrations", "circleci", "update", "-a", "test", "-i"])

@responses.activate
def test_integrations_circle_ci_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/circleci/configuration/validate/test", json={}, status=200)
    cli(["integrations", "circleci", "validate", "-a", "test"])

@responses.activate
def test_integrations_circle_ci_validate_all():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/circleci/configuration/validate", json={}, status=200)
    cli(["integrations", "circleci", "validate-all"])
