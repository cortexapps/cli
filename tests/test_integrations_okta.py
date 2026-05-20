from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_okta_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_okta_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/okta/configuration", json={}, status=200)
    cli(["integrations", "okta", "add", "-f", str(f)])

@responses.activate
def test_integrations_okta_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/okta/default-configuration", json={}, status=200)
    cli(["integrations", "okta", "get"])

@responses.activate
def test_integrations_okta_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/okta/configuration", json={}, status=200)
    cli(["integrations", "okta", "update", "-f", str(f)])

@responses.activate
def test_integrations_okta_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/okta/configuration/validate", json={}, status=200)
    cli(["integrations", "okta", "validate"])

@responses.activate
def test_integrations_okta_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/okta/configurations", json={}, status=200)
    cli(["integrations", "okta", "delete"])
