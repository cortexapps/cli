from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_azure_resources_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_azure_resources_add():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-resources/configuration", json=[{'accountId': 123, 'role:': 'test'}], status=200)
    cli(["integrations", "azure-resources", "add", "-a", "myAlias", "-h", "my.host.com", "-o", "my-slug", "-p", "123456", "-u", "steph.curry"])

@responses.activate
def test_integrations_azure_resources_add_multiple(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-resources/configurations", json={}, status=200)
    cli(["integrations", "azure-resources", "add-multiple", "-f", str(f)])

@responses.activate
def test_integrations_azure_resources_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-resources/configuration/test", status=200)
    cli(["integrations", "azure-resources", "delete", "-a", "test"])

@responses.activate
def test_integrations_azure_resources_delete_all():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-resources/configurations", status=200)
    cli(["integrations", "azure-resources", "delete-all"])

@responses.activate
def test_integrations_azure_resources_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-resources/configuration/test", json={}, status=200)
    cli(["integrations", "azure-resources", "get", "-a", "test"])

@responses.activate
def test_integrations_azure_resources_list():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-resources/configurations", json={}, status=200)
    cli(["integrations", "azure-resources", "list"])

@responses.activate
def test_integrations_azure_resources_get_default():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-resources/default-configuration", json={}, status=200)
    cli(["integrations", "azure-resources", "get-default"])

@responses.activate
def test_integrations_azure_resources_update():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-resources/configuration/test", json={}, status=200)
    cli(["integrations", "azure-resources", "update", "-a", "test", "-i"])

@responses.activate
def test_integrations_azure_resources_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-resources/configuration/validate/test", json={}, status=200)
    cli(["integrations", "azure-resources", "validate", "-a", "test"])

@responses.activate
def test_integrations_azure_resources_validate_all():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-resources/configuration/validate", json={}, status=200)
    cli(["integrations", "azure-resources", "validate-all"])

@responses.activate
def test_integrations_list_types():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-resoures/types", json={}, status=200)
    cli(["integrations", "azure-resources", "list-types"])

@responses.activate
def test_integrations_azure_resoures_update_types():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-resoures/types", json={}, status=200)
    cli(["integrations", "azure-resources", "update-types", "-t", "microsoft.insights/workbooks=true", "-t", "microsoft.resources/subscriptions=false"], ReturnType.RAW)
