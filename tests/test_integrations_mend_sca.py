from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_mend_sca_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_mend_sca_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/mend/sca/configuration", json={}, status=200)
    cli(["integrations", "mend-sca", "add", "-f", str(f)])

@responses.activate
def test_integrations_mend_sca_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/mend/sca/default-configuration", json={}, status=200)
    cli(["integrations", "mend-sca", "get"])

@responses.activate
def test_integrations_mend_sca_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/mend/sca/configuration", json={}, status=200)
    cli(["integrations", "mend-sca", "update", "-f", str(f)])

@responses.activate
def test_integrations_mend_sca_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/mend/sca/configuration/validate", json={}, status=200)
    cli(["integrations", "mend-sca", "validate"])

@responses.activate
def test_integrations_mend_sca_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/mend/sca/configurations", json={}, status=200)
    cli(["integrations", "mend-sca", "delete"])
