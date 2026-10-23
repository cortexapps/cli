from tests.helpers.utils import *
import os
import requests as _requests

# As part of this testing, filed:
# CET-19691: custom metrics POST API returns 200 response for un-processed metrics older than 6 months

def test():
    result = cli(["custom-metrics", "get", "-t", "cli-test-service", "-k", "vulnerabilities"], ReturnType.STDOUT)

    if "HTTP Error 403: Product access to [ENG_METRICS] not permitted" in result:
        print("API key does not have access to custom metrics or feature not enabled in tenant, not running tests.")
        return

    # 'vulnerabilities' must already exist as a metric definition; use `cortex custom-metrics definition-create` to create it.
    result = cli(["custom-metrics", "get", "-t", "cli-test-service", "-k", "vulnerabilities"], ReturnType.STDOUT)
    if "HTTP Error 404: Not Found - CustomMetricKey not found" in result:
        print("Custom metric named 'vulnerabilities' does not exist.  Create it with: cortex custom-metrics definition-create -k vulnerabilities -n Vulnerabilities -V POSITIVE")
        return

    date = today()
    cli(["custom-metrics", "delete", "-t", "cli-test-service", "-k", "vulnerabilities", "-s", "2022-01-01T00:00:00", "-e", today()])
    cli(["custom-metrics", "add", "-t", "cli-test-service", "-k", "vulnerabilities", "-v", "3.0"])
    result = cli(["custom-metrics", "get", "-t", "cli-test-service", "-k", "vulnerabilities"])
    assert result['data'][0]['value'] == 3.0, "should have single value of 3.0"

    cli(["custom-metrics", "add-in-bulk", "-t", "cli-test-service", "-k", "vulnerabilities", "-v", f"{date}=1.0", "-v", f"{date}=2.0"])
    result = cli(["custom-metrics", "get", "-t", "cli-test-service", "-k", "vulnerabilities"])
    assert result['total'] == 3, "should have total of 3 metrics data points"

def test_definition_create():
    # Skip if ENG_METRICS not enabled in tenant
    access_check = cli(["custom-metrics", "get", "-t", "cli-test-service", "-k", "vulnerabilities"], ReturnType.STDOUT)
    if "HTTP Error 403: Product access to [ENG_METRICS] not permitted" in access_check:
        print("Skipping - no Eng Metrics access")
        return

    base_url = os.environ.get("CORTEX_BASE_URL", "https://api.getcortexapp.com").rstrip("/")
    api_key = os.environ.get("CORTEX_API_KEY", "")
    # Pre-clean any leftover from a prior interrupted run (ignore result)
    _requests.delete(
        f"{base_url}/api/v1/eng-intel/custom-metrics/cli-test-definition",
        headers={"Authorization": f"Bearer {api_key}"},
    )

    result = cli(["custom-metrics", "definition-create",
                  "-k", "cli-test-definition",
                  "-n", "CLI Test Definition",
                  "-V", "POSITIVE",
                  "-c", "Test",
                  "-d", "Temporary definition for CLI testing",
                  "--is-draft"])
    assert result["key"] == "cli-test-definition"
    assert result["name"] == "CLI Test Definition"
    assert result["valence"] == "POSITIVE"
    assert result["category"] == "Test"
    assert result["description"] == "Temporary definition for CLI testing"
    assert result["isDraft"] is True
    assert result["type"] == "PUBLIC_API"
