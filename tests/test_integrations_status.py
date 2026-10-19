from tests.helpers.utils import *

@responses.activate
def test_integrations_status():
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/integrations/status", json={"integrations": []}, status=200)
    result = cli(["integrations", "status"])
    assert "integrations" in result
