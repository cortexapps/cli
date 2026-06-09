from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_sentry_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_sentry_add(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/sentry/configuration", json={}, status=200)
    cli(["integrations", "sentry", "add", "-f", str(f)])

@responses.activate
def test_integrations_sentry_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/sentry/default-configuration", json={}, status=200)
    cli(["integrations", "sentry", "get"])

@responses.activate
def test_integrations_sentry_update(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/sentry/configuration", json={}, status=200)
    cli(["integrations", "sentry", "update", "-f", str(f)])

@responses.activate
def test_integrations_sentry_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/sentry/configuration/validate", json={}, status=200)
    cli(["integrations", "sentry", "validate"])

@responses.activate
def test_integrations_sentry_add_with_flags():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/sentry/configuration", json={}, status=200)
    cli(["integrations", "sentry", "add", "--auth-token", "foo", "--organization-slug", "bar"])

@responses.activate
def test_integrations_sentry_add_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "sentry", "add", "-f", str(f), "--auth-token", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_sentry_update_with_flags():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/sentry/configuration", json={}, status=200)
    cli(["integrations", "sentry", "update", "--auth-token", "foo"])

@responses.activate
def test_integrations_sentry_update_file_with_flags_error(tmp_path):
    f = _dummy_file(tmp_path)
    result = cli(["integrations", "sentry", "update", "-f", str(f), "--auth-token", "foo"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_integrations_sentry_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/sentry/configurations", json={}, status=200)
    cli(["integrations", "sentry", "delete"])
