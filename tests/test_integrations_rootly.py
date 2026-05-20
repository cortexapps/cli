from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_rootly_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_rootly_add():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/rootly/configuration", json={}, status=200)
    cli(["integrations", "rootly", "add", "-a", "myAlias", "--api-key", "123456", "-i"])

@responses.activate
def test_integrations_rootly_add_multiple(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/rootly/configurations", json={}, status=200)
    cli(["integrations", "rootly", "add-multiple", "-f", str(f)])

@responses.activate
def test_integrations_rootly_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/rootly/configuration/test", status=200)
    cli(["integrations", "rootly", "delete", "-a", "test"])

@responses.activate
def test_integrations_rootly_delete_all():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/rootly/configurations", status=200)
    cli(["integrations", "rootly", "delete-all"])

@responses.activate
def test_integrations_rootly_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/rootly/configuration/test", json={}, status=200)
    cli(["integrations", "rootly", "get", "-a", "test"])

@responses.activate
def test_integrations_rootly_list():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/rootly/configurations", json={}, status=200)
    cli(["integrations", "rootly", "list"])

@responses.activate
def test_integrations_rootly_get_default():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/rootly/default-configuration", json={}, status=200)
    cli(["integrations", "rootly", "get-default"])

@responses.activate
def test_integrations_rootly_update():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/rootly/configuration/test", json={}, status=200)
    cli(["integrations", "rootly", "update", "-a", "test", "-i"])

@responses.activate
def test_integrations_rootly_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/rootly/configuration/validate/test", json={}, status=200)
    cli(["integrations", "rootly", "validate", "-a", "test"])

@responses.activate
def test_integrations_rootly_validate_all():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/rootly/configuration/validate", json={}, status=200)
    cli(["integrations", "rootly", "validate-all"])
