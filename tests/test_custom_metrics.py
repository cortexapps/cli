from tests.helpers.utils import *

# As part of this testing, filed:
# CET-19691: custom metrics POST API returns 200 response for un-processed metrics older than 6 months

def test():
    result = cli(["custom-metrics", "get", "-t", "cli-test-service", "-k", "vulnerabilities"], ReturnType.STDOUT)

    if "HTTP Error 403: Product access to [ENG_METRICS] not permitted" in result:
        print("API key does not have access to custom metrics or feature not enabled in tenant, not running tests.")
        return

    # No API support to create a custom metric.  It can only be done in the UI, so check if this workspace has the
    # 'vulnerabilities' custom metric defined.
    result = cli(["custom-metrics", "get", "-t", "cli-test-service", "-k", "vulnerabilities"], ReturnType.STDOUT)
    if "HTTP Error 404: Not Found - CustomMetricKey not found" in result:
        print("Custom metric named 'vulnerabilities' does not exist.  It has to be created in the UI for this test to run.")
        print("To create: Settings -> Eng Intelligence -> General -> Custom -> Add Metric -> (select API toggle).")
        return

    date = today()
    cli(["custom-metrics", "delete", "-t", "cli-test-service", "-k", "vulnerabilities", "-s", "2022-01-01T00:00:00", "-e", today()])
    cli(["custom-metrics", "add", "-t", "cli-test-service", "-k", "vulnerabilities", "-v", "3.0"])
    result = cli(["custom-metrics", "get", "-t", "cli-test-service", "-k", "vulnerabilities"])
    assert result['data'][0]['value'] == 3.0, "should have single value of 3.0"

    cli(["custom-metrics", "add-in-bulk", "-t", "cli-test-service", "-k", "vulnerabilities", "-v", f"{date}=1.0", "-v", f"{date}=2.0"])
    result = cli(["custom-metrics", "get", "-t", "cli-test-service", "-k", "vulnerabilities"])
    assert result['total'] == 3, "should have total of 3 metrics data points"
