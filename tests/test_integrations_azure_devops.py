from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_azure_devops_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_azure_devops_add():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-devops/configuration", json=[{'accountId': 123, 'role:': 'test'}], status=200)
    cli(["integrations", "azure-devops", "add", "-a", "myAlias", "-h", "my.host.com", "-o", "my-slug", "-p", "123456", "-u", "steph.curry"])

@responses.activate
def test_integrations_azure_devops_add_multiple(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-devops/configurations", json={}, status=200)
    cli(["integrations", "azure-devops", "add-multiple", "-f", str(f)])

@responses.activate
def test_integrations_azure_devops_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-devops/configuration/test", status=200)
    cli(["integrations", "azure-devops", "delete", "-a", "test"])

@responses.activate
def test_integrations_azure_devops_delete_all():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-devops/configurations", status=200)
    cli(["integrations", "azure-devops", "delete-all"])

@responses.activate
def test_integrations_azure_devops_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-devops/configuration/test", json={}, status=200)
    cli(["integrations", "azure-devops", "get", "-a", "test"])

@responses.activate
def test_integrations_azure_devops_get_all():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-devops/configurations", json={}, status=200)
    cli(["integrations", "azure-devops", "get-all"])

@responses.activate
def test_integrations_azure_devops_get_default():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-devops/default-configuration", json={}, status=200)
    cli(["integrations", "azure-devops", "get-default"])

@responses.activate
def test_integrations_azure_devops_update():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-devops/configuration/test", json={}, status=200)
    cli(["integrations", "azure-devops", "update", "-a", "test", "-i"])

@responses.activate
def test_integrations_azure_devops_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-devops/configuration/validate/test", json={}, status=200)
    cli(["integrations", "azure-devops", "validate", "-a", "test"])

@responses.activate
def test_integrations_azure_devops_validate_all():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-devops/configuration/validate", json={}, status=200)
    cli(["integrations", "azure-devops", "validate-all"])
