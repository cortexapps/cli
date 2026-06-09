from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_firehydrant_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_firehydrant_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/firehydrant/configuration", json={}, status=200)
    cli(["integrations", "firehydrant", "add", "-f", str(f)])

@responses.activate
def test_integrations_firehydrant_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/firehydrant/default-configuration", json={}, status=200)
    cli(["integrations", "firehydrant", "get"])

@responses.activate
def test_integrations_firehydrant_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/firehydrant/configuration", json={}, status=200)
    cli(["integrations", "firehydrant", "update", "-f", str(f)])

@responses.activate
def test_integrations_firehydrant_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/firehydrant/configuration/validate", json={}, status=200)
    cli(["integrations", "firehydrant", "validate"])

@responses.activate
def test_integrations_firehydrant_add_with_flags():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/firehydrant/configuration", json={}, status=200)
    cli(["integrations", "firehydrant", "add", "--api-token", "foo"])

@responses.activate
def test_integrations_firehydrant_add_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "firehydrant", "add", "-f", str(f), "--api-token", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_firehydrant_update_with_flags():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/firehydrant/configuration", json={}, status=200)
    cli(["integrations", "firehydrant", "update", "--api-token", "foo"])

@responses.activate
def test_integrations_firehydrant_update_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "firehydrant", "update", "-f", str(f), "--api-token", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_firehydrant_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/firehydrant/configurations", json={}, status=200)
    cli(["integrations", "firehydrant", "delete"])
