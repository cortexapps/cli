"""
Tests for incident.io integration commands.

These tests all use mock responses.
"""
from cortexapps_cli.cortex import cli
import json
import responses

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_incidentio_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_incidentio_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, "https://api.getcortexapp.com/api/v1/incidentio/configuration", json=[{'accountId': 123, 'alias:': 'test', 'isDefault': json.dumps("true"), 'personalKey': 'xxxx', 'region': 'US'}], status=200)
    cli(["integrations", "incidentio", "add", "-f", str(f)])

@responses.activate
def test_integrations_incidentio_add_multiple(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, "https://api.getcortexapp.com/api/v1/incidentio/configurations", json=[{'accountId': 123, 'alias:': 'test', 'isDefault': json.dumps("true"), 'personalKey': 'xxxx', 'region': 'US'}], status=200)
    cli(["integrations", "incidentio", "add-multiple", "-f", str(f)])

@responses.activate
def test_integrations_incidentio_delete():
    responses.add(responses.DELETE, "https://api.getcortexapp.com/api/v1/incidentio/configuration/test", status=200)
    cli(["integrations", "incidentio", "delete", "-a", "test"])

@responses.activate
def test_integrations_incidentio_delete_all():
    responses.add(responses.DELETE, "https://api.getcortexapp.com/api/v1/incidentio/configurations", status=200)
    cli(["integrations", "incidentio", "delete-all"])

@responses.activate
def test_integrations_incidentio_get():
    responses.add(responses.GET, "https://api.getcortexapp.com/api/v1/incidentio/configuration/test", json=[{'accountId': 123, 'alias:': 'test', 'isDefault': json.dumps("true"), 'personalKey': 'xxxx', 'region': 'US'}], status=200)
    cli(["integrations", "incidentio", "get", "-a", "test"])

@responses.activate
def test_integrations_incidentio_get_all():
    responses.add(responses.GET, "https://api.getcortexapp.com/api/v1/incidentio/configurations", json=[{'accountId': 123, 'alias:': 'test', 'isDefault': json.dumps("true"), 'personalKey': 'xxxx', 'region': 'US'}], status=200)
    cli(["integrations", "incidentio", "get-all"])

@responses.activate
def test_integrations_incidentio_get_default():
    responses.add(responses.GET, "https://api.getcortexapp.com/api/v1/incidentio/default-configuration", json=[{'accountId': 123, 'alias:': 'test', 'isDefault': json.dumps("true"), 'personalKey': 'xxxx', 'region': 'US'}], status=200)
    cli(["integrations", "incidentio", "get-default"])

@responses.activate
def test_integrations_incidentio_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, "https://api.getcortexapp.com/api/v1/incidentio/configuration/test", json=[{'alias:': 'test', 'isDefault': json.dumps("true")}], status=200)
    cli(["integrations", "incidentio", "update", "-a", "test", "-f", str(f)])

@responses.activate
def test_integrations_incidentio_validate():
    responses.add(responses.POST, "https://api.getcortexapp.com/api/v1/incidentio/configuration/validate/test", json={'alias': 'test', 'isValid': json.dumps("true"), 'message': 'someMessage'}, status=200)
    cli(["integrations", "incidentio", "validate", "-a", "test"])

@responses.activate
def test_integrations_incidentio_validate_all():
    responses.add(responses.POST, "https://api.getcortexapp.com/api/v1/incidentio/configuration/validate", json=[ { 'alias': 'test', 'isValid': json.dumps("true"), 'message': 'someMessage'}], status=200)
    cli(["integrations", "incidentio", "validate-all"])
