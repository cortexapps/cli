from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_launchdarkly_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_launchdarkly_add():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/launchdarkly/configuration", json={}, status=200)
    cli(["integrations", "launchdarkly", "add", "-a", "myAlias", "-h", "my.host.com", "--api-key", "123456", "-i"])

@responses.activate
def test_integrations_launchdarkly_add_multiple(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/launchdarkly/configurations", json={}, status=200)
    cli(["integrations", "launchdarkly", "add-multiple", "-f", str(f)])

@responses.activate
def test_integrations_launchdarkly_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/launchdarkly/configuration/test", status=200)
    cli(["integrations", "launchdarkly", "delete", "-a", "test"])

@responses.activate
def test_integrations_launchdarkly_delete_all():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/launchdarkly/configurations", status=200)
    cli(["integrations", "launchdarkly", "delete-all"])

@responses.activate
def test_integrations_launchdarkly_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/launchdarkly/configuration/test", json={}, status=200)
    cli(["integrations", "launchdarkly", "get", "-a", "test"])

@responses.activate
def test_integrations_launchdarkly_get_all():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/launchdarkly/configurations", json={}, status=200)
    cli(["integrations", "launchdarkly", "get-all"])

@responses.activate
def test_integrations_launchdarkly_get_default():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/launchdarkly/default-configuration", json={}, status=200)
    cli(["integrations", "launchdarkly", "get-default"])

@responses.activate
def test_integrations_launchdarkly_update():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/launchdarkly/configuration/test", json={}, status=200)
    cli(["integrations", "launchdarkly", "update", "-a", "test", "-i"])

@responses.activate
def test_integrations_launchdarkly_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/launchdarkly/configuration/validate/test", json={}, status=200)
    cli(["integrations", "launchdarkly", "validate", "-a", "test"])

@responses.activate
def test_integrations_launchdarkly_validate_all():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/launchdarkly/configuration/validate", json={}, status=200)
    cli(["integrations", "launchdarkly", "validate-all"])
