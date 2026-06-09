from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_veracode_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_veracode_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/veracode/configuration", json={}, status=200)
    cli(["integrations", "veracode", "add", "-f", str(f)])

@responses.activate
def test_integrations_veracode_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/veracode/default-configuration", json={}, status=200)
    cli(["integrations", "veracode", "get"])

@responses.activate
def test_integrations_veracode_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/veracode/configuration", json={}, status=200)
    cli(["integrations", "veracode", "update", "-f", str(f)])

@responses.activate
def test_integrations_veracode_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/veracode/configuration/validate", json={}, status=200)
    cli(["integrations", "veracode", "validate"])

@responses.activate
def test_integrations_veracode_add_with_flags():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/veracode/configuration", json={}, status=200)
    cli(["integrations", "veracode", "add", "--api-key", "foo", "--key-id", "bar", "--region", "baz"])

@responses.activate
def test_integrations_veracode_add_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "veracode", "add", "-f", str(f), "--api-key", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_veracode_update_with_flags():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/veracode/configuration", json={}, status=200)
    cli(["integrations", "veracode", "update", "--api-key", "foo"])

@responses.activate
def test_integrations_veracode_update_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "veracode", "update", "-f", str(f), "--api-key", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_veracode_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/veracode/configurations", json={}, status=200)
    cli(["integrations", "veracode", "delete"])
