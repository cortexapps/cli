from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_azure_active_directory_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_azure_active_directory_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/active-directory/configuration", json={}, status=200)
    cli(["integrations", "azure-active-directory", "add", "-f", str(f)])

@responses.activate
def test_integrations_azure_active_directory_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/active-directory/default-configuration", json={}, status=200)
    cli(["integrations", "azure-active-directory", "get"])

@responses.activate
def test_integrations_azure_active_directory_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/active-directory/configuration", json={}, status=200)
    cli(["integrations", "azure-active-directory", "update", "-f", str(f)])

@responses.activate
def test_integrations_azure_active_directory_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/active-directory/configuration/validate", json={}, status=200)
    cli(["integrations", "azure-active-directory", "validate"])

@responses.activate
def test_integrations_azure_active_directory_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/active-directory/configurations", json={}, status=200)
    cli(["integrations", "azure-active-directory", "delete"])
