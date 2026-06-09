from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_sumologic_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_sumologic_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/sumologic/configuration", json={}, status=200)
    cli(["integrations", "sumo-logic", "add", "-f", str(f)])

@responses.activate
def test_integrations_sumologic_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/sumologic/default-configuration", json={}, status=200)
    cli(["integrations", "sumo-logic", "get"])

@responses.activate
def test_integrations_sumologic_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/sumologic/configuration", json={}, status=200)
    cli(["integrations", "sumo-logic", "update", "-f", str(f)])

@responses.activate
def test_integrations_sumologic_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/sumologic/configuration/validate", json={}, status=200)
    cli(["integrations", "sumo-logic", "validate"])

@responses.activate
def test_integrations_sumologic_add_with_flags():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/sumologic/configuration", json={}, status=200)
    cli(["integrations", "sumo-logic", "add", "--access-id", "foo", "--access-key", "bar", "--deployment", "baz"])

@responses.activate
def test_integrations_sumologic_add_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "sumo-logic", "add", "-f", str(f), "--access-id", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_sumologic_update_with_flags():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/sumologic/configuration", json={}, status=200)
    cli(["integrations", "sumo-logic", "update", "--access-id", "foo"])

@responses.activate
def test_integrations_sumologic_update_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "sumo-logic", "update", "-f", str(f), "--access-id", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_sumologic_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/sumologic/configurations", json={}, status=200)
    cli(["integrations", "sumo-logic", "delete"])
