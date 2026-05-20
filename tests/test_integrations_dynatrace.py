from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_dynatrace_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_dynatrace_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/dynatrace/configuration", json={}, status=200)
    cli(["integrations", "dynatrace", "add", "-f", str(f)])

@responses.activate
def test_integrations_dynatrace_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/dynatrace/default-configuration", json={}, status=200)
    cli(["integrations", "dynatrace", "get"])

@responses.activate
def test_integrations_dynatrace_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/dynatrace/configuration", json={}, status=200)
    cli(["integrations", "dynatrace", "update", "-f", str(f)])

@responses.activate
def test_integrations_dynatrace_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/dynatrace/configuration/validate", json={}, status=200)
    cli(["integrations", "dynatrace", "validate"])

@responses.activate
def test_integrations_dynatrace_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/dynatrace/configurations", json={}, status=200)
    cli(["integrations", "dynatrace", "delete"])
