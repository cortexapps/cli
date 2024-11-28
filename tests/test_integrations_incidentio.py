from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_incidentio_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_incidentio_add():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/incidentio/configuration", json={}, status=200)
    cli(["integrations", "incidentio", "add", "-a", "myAlias", "-h", "my.host.com", "--api-key", "123456", "-i"])

@responses.activate
def test_integrations_incidentio_add_multiple(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/incidentio/configurations", json={}, status=200)
    cli(["integrations", "incidentio", "add-multiple", "-f", str(f)])

@responses.activate
def test_integrations_incidentio_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/incidentio/configuration/test", status=200)
    cli(["integrations", "incidentio", "delete", "-a", "test"])

@responses.activate
def test_integrations_incidentio_delete_all():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/incidentio/configurations", status=200)
    cli(["integrations", "incidentio", "delete-all"])

@responses.activate
def test_integrations_incidentio_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/incidentio/configuration/test", json={}, status=200)
    cli(["integrations", "incidentio", "get", "-a", "test"])

@responses.activate
def test_integrations_incidentio_get_all():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/incidentio/configurations", json={}, status=200)
    cli(["integrations", "incidentio", "get-all"])

@responses.activate
def test_integrations_incidentio_get_default():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/incidentio/default-configuration", json={}, status=200)
    cli(["integrations", "incidentio", "get-default"])

@responses.activate
def test_integrations_incidentio_update():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/incidentio/configuration/test", json={}, status=200)
    cli(["integrations", "incidentio", "update", "-a", "test", "-i"])

@responses.activate
def test_integrations_incidentio_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/incidentio/configuration/validate/test", json={}, status=200)
    cli(["integrations", "incidentio", "validate", "-a", "test"])

@responses.activate
def test_integrations_incidentio_validate_all():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/incidentio/configuration/validate", json={}, status=200)
    cli(["integrations", "incidentio", "validate-all"])
