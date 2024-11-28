from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_coralogix_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_coralogix_add():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/coralogix/configuration", json={}, status=200)
    cli(["integrations", "coralogix", "add", "-a", "myAlias", "-r", "US1", "--api-key", "123456", "-i"])

@responses.activate
def test_integrations_coralogix_add_multiple(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/coralogix/configurations", json={}, status=200)
    cli(["integrations", "coralogix", "add-multiple", "-f", str(f)])

@responses.activate
def test_integrations_coralogix_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/coralogix/configuration/test", status=200)
    cli(["integrations", "coralogix", "delete", "-a", "test"])

@responses.activate
def test_integrations_coralogix_delete_all():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/coralogix/configurations", status=200)
    cli(["integrations", "coralogix", "delete-all"])

@responses.activate
def test_integrations_coralogix_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/coralogix/configuration/test", json={}, status=200)
    cli(["integrations", "coralogix", "get", "-a", "test"])

@responses.activate
def test_integrations_coralogix_get_all():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/coralogix/configurations", json={}, status=200)
    cli(["integrations", "coralogix", "get-all"])

@responses.activate
def test_integrations_coralogix_get_default():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/coralogix/default-configuration", json={}, status=200)
    cli(["integrations", "coralogix", "get-default"])

@responses.activate
def test_integrations_coralogix_update():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/coralogix/configuration/test", json={}, status=200)
    cli(["integrations", "coralogix", "update", "-a", "test", "-i"])

@responses.activate
def test_integrations_coralogix_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/coralogix/configuration/validate/test", json={}, status=200)
    cli(["integrations", "coralogix", "validate", "-a", "test"])

@responses.activate
def test_integrations_coralogix_validate_all():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/coralogix/configuration/validate", json={}, status=200)
    cli(["integrations", "coralogix", "validate-all"])
