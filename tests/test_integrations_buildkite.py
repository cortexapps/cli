from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_buildkite_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_buildkite_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/buildkite/configuration", json={}, status=200)
    cli(["integrations", "buildkite", "add", "-f", str(f)])

@responses.activate
def test_integrations_buildkite_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/buildkite/default-configuration", json={}, status=200)
    cli(["integrations", "buildkite", "get"])

@responses.activate
def test_integrations_buildkite_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/buildkite/configuration", json={}, status=200)
    cli(["integrations", "buildkite", "update", "-f", str(f)])

@responses.activate
def test_integrations_buildkite_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/buildkite/configuration/validate", json={}, status=200)
    cli(["integrations", "buildkite", "validate"])

@responses.activate
def test_integrations_buildkite_add_with_flags():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/buildkite/configuration", json={}, status=200)
    cli(["integrations", "buildkite", "add", "--api-token", "foo", "--organization-slug", "bar"])

@responses.activate
def test_integrations_buildkite_add_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "buildkite", "add", "-f", str(f), "--api-token", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_buildkite_update_with_flags():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/buildkite/configuration", json={}, status=200)
    cli(["integrations", "buildkite", "update", "--api-token", "foo"])

@responses.activate
def test_integrations_buildkite_update_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "buildkite", "update", "-f", str(f), "--api-token", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_buildkite_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/buildkite/configurations", json={}, status=200)
    cli(["integrations", "buildkite", "delete"])
