from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_mend_sast_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_mend_sast_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/mend/sast/configuration", json={}, status=200)
    cli(["integrations", "mend-sast", "add", "-f", str(f)])

@responses.activate
def test_integrations_mend_sast_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/mend/sast/default-configuration", json={}, status=200)
    cli(["integrations", "mend-sast", "get"])

@responses.activate
def test_integrations_mend_sast_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/mend/sast/configuration", json={}, status=200)
    cli(["integrations", "mend-sast", "update", "-f", str(f)])

@responses.activate
def test_integrations_mend_sast_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/mend/sast/configuration/validate", json={}, status=200)
    cli(["integrations", "mend-sast", "validate"])

@responses.activate
def test_integrations_mend_sast_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/mend/sast/configurations", json={}, status=200)
    cli(["integrations", "mend-sast", "delete"])
