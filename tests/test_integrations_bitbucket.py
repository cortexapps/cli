from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_bitbucket_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_bitbucket_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/bitbucket/configuration", json={}, status=200)
    cli(["integrations", "bitbucket", "add", "-f", str(f)])

@responses.activate
def test_integrations_bitbucket_add_multiple(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/bitbucket/configurations", json={}, status=200)
    cli(["integrations", "bitbucket", "add-multiple", "-f", str(f)])

@responses.activate
def test_integrations_bitbucket_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/bitbucket/configuration/test", status=200)
    cli(["integrations", "bitbucket", "delete", "-a", "test"])

@responses.activate
def test_integrations_bitbucket_delete_all():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/bitbucket/configurations", status=200)
    cli(["integrations", "bitbucket", "delete-all"])

@responses.activate
def test_integrations_bitbucket_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/bitbucket/configuration/test", json={}, status=200)
    cli(["integrations", "bitbucket", "get", "-a", "test"])

@responses.activate
def test_integrations_bitbucket_list():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/bitbucket/configurations", json={}, status=200)
    cli(["integrations", "bitbucket", "list"])

@responses.activate
def test_integrations_bitbucket_get_default():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/bitbucket/default-configuration", json={}, status=200)
    cli(["integrations", "bitbucket", "get-default"])

@responses.activate
def test_integrations_bitbucket_update():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/bitbucket/configuration/test", json={}, status=200)
    cli(["integrations", "bitbucket", "update", "-a", "test", "-i"])

@responses.activate
def test_integrations_bitbucket_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/bitbucket/configuration/validate/test", json={}, status=200)
    cli(["integrations", "bitbucket", "validate", "-a", "test"])

@responses.activate
def test_integrations_bitbucket_validate_all():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/bitbucket/configuration/validate", json={}, status=200)
    cli(["integrations", "bitbucket", "validate-all"])
