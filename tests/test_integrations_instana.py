from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_instana_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_instana_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/instana/configuration", json={}, status=200)
    cli(["integrations", "instana", "add", "-f", str(f)])

@responses.activate
def test_integrations_instana_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/instana/default-configuration", json={}, status=200)
    cli(["integrations", "instana", "get"])

@responses.activate
def test_integrations_instana_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/instana/configuration", json={}, status=200)
    cli(["integrations", "instana", "update", "-f", str(f)])

@responses.activate
def test_integrations_instana_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/instana/configuration/validate", json={}, status=200)
    cli(["integrations", "instana", "validate"])

@responses.activate
def test_integrations_instana_add_with_flags():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/instana/configuration", json={}, status=200)
    cli(["integrations", "instana", "add", "--api-token", "foo", "--endpoint", "bar"])

@responses.activate
def test_integrations_instana_add_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "instana", "add", "-f", str(f), "--api-token", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_instana_update_with_flags():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/instana/configuration", json={}, status=200)
    cli(["integrations", "instana", "update", "--api-token", "foo"])

@responses.activate
def test_integrations_instana_update_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "instana", "update", "-f", str(f), "--api-token", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_instana_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/instana/configurations", json={}, status=200)
    cli(["integrations", "instana", "delete"])
