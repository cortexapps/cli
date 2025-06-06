from tests.helpers.utils import *

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test_integrations_prometheus_add.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_prometheus_add():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/prometheus/configuration", json={}, status=200)
    cli(["integrations", "prometheus", "add", "-a", "myAlias", "-h", "my.host.com", "--api-key", "123456", "-i"])

@responses.activate
def test_integrations_prometheus_add_multiple(tmp_path):
    f = _dummy_file(tmp_path)
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/prometheus/configurations", json={}, status=200)
    cli(["integrations", "prometheus", "add-multiple", "-f", str(f)])

@responses.activate
def test_integrations_prometheus_delete():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/prometheus/configuration/test", status=200)
    cli(["integrations", "prometheus", "delete", "-a", "test"])

@responses.activate
def test_integrations_prometheus_delete_all():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/prometheus/configurations", status=200)
    cli(["integrations", "prometheus", "delete-all"])

@responses.activate
def test_integrations_prometheus_get():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/prometheus/configuration/test", json={}, status=200)
    cli(["integrations", "prometheus", "get", "-a", "test"])

@responses.activate
def test_integrations_prometheus_list():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/prometheus/configurations", json={}, status=200)
    cli(["integrations", "prometheus", "list"])

@responses.activate
def test_integrations_prometheus_get_default():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/prometheus/default-configuration", json={}, status=200)
    cli(["integrations", "prometheus", "get-default"])

@responses.activate
def test_integrations_prometheus_update():
    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/prometheus/configuration/test", json={}, status=200)
    cli(["integrations", "prometheus", "update", "-a", "test", "-i"])

@responses.activate
def test_integrations_prometheus_validate():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/prometheus/configuration/validate/test", json={}, status=200)
    cli(["integrations", "prometheus", "validate", "-a", "test"])

@responses.activate
def test_integrations_prometheus_validate_all():
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/prometheus/configuration/validate", json={}, status=200)
    cli(["integrations", "prometheus", "validate-all"])
