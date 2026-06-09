from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_wiz_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_wiz_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/wiz/configuration", json={}, status=200)
    cli(["integrations", "wiz", "add", "-f", str(f)])

@responses.activate
def test_integrations_wiz_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/wiz/default-configuration", json={}, status=200)
    cli(["integrations", "wiz", "get"])

@responses.activate
def test_integrations_wiz_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/wiz/configuration", json={}, status=200)
    cli(["integrations", "wiz", "update", "-f", str(f)])

@responses.activate
def test_integrations_wiz_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/wiz/configuration/validate", json={}, status=200)
    cli(["integrations", "wiz", "validate"])

@responses.activate
def test_integrations_wiz_add_with_flags():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/wiz/configuration", json={}, status=200)
    cli(["integrations", "wiz", "add", "--client-id", "foo", "--client-secret", "bar", "--data-center", "baz", "--identity-provider", "qux"])

@responses.activate
def test_integrations_wiz_add_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "wiz", "add", "-f", str(f), "--client-id", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_wiz_update_with_flags():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/wiz/configuration", json={}, status=200)
    cli(["integrations", "wiz", "update", "--client-id", "foo"])

@responses.activate
def test_integrations_wiz_update_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "wiz", "update", "-f", str(f), "--client-id", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_wiz_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/wiz/configurations", json={}, status=200)
    cli(["integrations", "wiz", "delete"])
