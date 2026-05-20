from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_codecov_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_codecov_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/codecov/configuration", json={}, status=200)
    cli(["integrations", "codecov", "add", "-f", str(f)])

@responses.activate
def test_integrations_codecov_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/codecov/default-configuration", json={}, status=200)
    cli(["integrations", "codecov", "get"])

@responses.activate
def test_integrations_codecov_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/codecov/configuration", json={}, status=200)
    cli(["integrations", "codecov", "update", "-f", str(f)])

@responses.activate
def test_integrations_codecov_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/codecov/configuration/validate", json={}, status=200)
    cli(["integrations", "codecov", "validate"])

@responses.activate
def test_integrations_codecov_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/codecov/configurations", json={}, status=200)
    cli(["integrations", "codecov", "delete"])
