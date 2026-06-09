from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_checkmarx_sast_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_checkmarx_sast_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/checkmarx/sast/configuration", json={}, status=200)
    cli(["integrations", "checkmarx-sast", "add", "-f", str(f)])

@responses.activate
def test_integrations_checkmarx_sast_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/checkmarx/sast/default-configuration", json={}, status=200)
    cli(["integrations", "checkmarx-sast", "get"])

@responses.activate
def test_integrations_checkmarx_sast_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/checkmarx/sast/configuration", json={}, status=200)
    cli(["integrations", "checkmarx-sast", "update", "-f", str(f)])

@responses.activate
def test_integrations_checkmarx_sast_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/checkmarx/sast/configuration/validate", json={}, status=200)
    cli(["integrations", "checkmarx-sast", "validate"])

@responses.activate
def test_integrations_checkmarx_sast_add_with_flags():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/checkmarx/sast/configuration", json={}, status=200)
    cli(["integrations", "checkmarx-sast", "add", "--username", "foo", "--password", "bar"])

@responses.activate
def test_integrations_checkmarx_sast_add_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "checkmarx-sast", "add", "-f", str(f), "--username", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_checkmarx_sast_update_with_flags():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/checkmarx/sast/configuration", json={}, status=200)
    cli(["integrations", "checkmarx-sast", "update", "--username", "foo"])

@responses.activate
def test_integrations_checkmarx_sast_update_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "checkmarx-sast", "update", "-f", str(f), "--username", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_checkmarx_sast_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/checkmarx/sast/configurations", json={}, status=200)
    cli(["integrations", "checkmarx-sast", "delete"])
