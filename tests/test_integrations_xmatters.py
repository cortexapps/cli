from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_xmatters_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_xmatters_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/xmatters/configuration", json={}, status=200)
    cli(["integrations", "xmatters", "add", "-f", str(f)])

@responses.activate
def test_integrations_xmatters_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/xmatters/default-configuration", json={}, status=200)
    cli(["integrations", "xmatters", "get"])

@responses.activate
def test_integrations_xmatters_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/xmatters/configuration", json={}, status=200)
    cli(["integrations", "xmatters", "update", "-f", str(f)])

@responses.activate
def test_integrations_xmatters_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/xmatters/configuration/validate", json={}, status=200)
    cli(["integrations", "xmatters", "validate"])

@responses.activate
def test_integrations_xmatters_add_with_flags():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/xmatters/configuration", json={}, status=200)
    cli(["integrations", "xmatters", "add", "--organization-slug", "foo", "--password", "bar", "--username", "baz"])

@responses.activate
def test_integrations_xmatters_add_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "xmatters", "add", "-f", str(f), "--organization-slug", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_xmatters_update_with_flags():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/xmatters/configuration", json={}, status=200)
    cli(["integrations", "xmatters", "update", "--organization-slug", "foo"])

@responses.activate
def test_integrations_xmatters_update_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "xmatters", "update", "-f", str(f), "--organization-slug", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_xmatters_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/xmatters/configurations", json={}, status=200)
    cli(["integrations", "xmatters", "delete"])
