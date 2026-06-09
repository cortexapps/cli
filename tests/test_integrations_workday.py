from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_workday_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_workday_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/workday/configuration", json={}, status=200)
    cli(["integrations", "workday", "add", "-f", str(f)])

@responses.activate
def test_integrations_workday_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/workday/default-configuration", json={}, status=200)
    cli(["integrations", "workday", "get"])

@responses.activate
def test_integrations_workday_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/workday/configuration", json={}, status=200)
    cli(["integrations", "workday", "update", "-f", str(f)])

@responses.activate
def test_integrations_workday_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/workday/configuration/validate", json={}, status=200)
    cli(["integrations", "workday", "validate"])

@responses.activate
def test_integrations_workday_add_with_flags():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/workday/configuration", json={}, status=200)
    cli(["integrations", "workday", "add", "--username", "foo", "--password", "bar", "--ownership-report-url", "baz"])

@responses.activate
def test_integrations_workday_add_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "workday", "add", "-f", str(f), "--username", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_workday_update_with_flags():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/workday/configuration", json={}, status=200)
    cli(["integrations", "workday", "update", "--username", "foo"])

@responses.activate
def test_integrations_workday_update_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "workday", "update", "-f", str(f), "--username", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_workday_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/workday/configurations", json={}, status=200)
    cli(["integrations", "workday", "delete"])
