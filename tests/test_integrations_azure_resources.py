"""
Tests for azure-resources integration commands.

These tests all use mock responses.
"""
from cortexapps_cli.cortex import cli
import os
import responses

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_azure_resources_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_azure_resources_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-resources/configuration", json={}, status=200)
    cli(["integrations", "azure-resources", "add", "-f", str(f)])

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
def test_integrations_azure_resources_get_all():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-resources/configurations", json={}, status=200)
    cli(["integrations", "azure-resources", "get-all"])

@responses.activate
def test_integrations_azure_resources_get_default():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-resources/default-configuration", json={}, status=200)
    cli(["integrations", "azure-resources", "get-default"])

@responses.activate
def test_integrations_azure_resources_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-resources/configuration/test", json={}, status=200)
    cli(["integrations", "azure-resources", "update", "-a", "test", "-f", str(f)])

@responses.activate
def test_integrations_azure_resources_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-resources/configuration/validate/test", json={}, status=200)
    cli(["integrations", "azure-resources", "validate", "-a", "test"])

@responses.activate
def test_integrations_azure_resources_validate_all():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/azure-resources/configuration/validate", json={}, status=200)
    cli(["integrations", "azure-resources", "validate-all"])
