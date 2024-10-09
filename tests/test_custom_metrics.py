from tests.helpers.utils import *

def test():
    cli(["custom-metrics", "delete", "-t", "shipping-integrations", "-k", "vulnerabilities", "-s", "2022-01-01T00:00:00", "-e", today()])
    cli(["custom-metrics", "add", "-t", "shipping-integrations", "-k", "vulnerabilities", "-v", "3.0"])
    result = cli(["custom-metrics", "get", "-t", "shipping-integrations", "-k", "vulnerabilities"])
    assert result['data'][0]['value'] == 3.0, "should have single value of 3.0"

    cli(["custom-metrics", "add-in-bulk", "-t", "shipping-integrations", "-k", "vulnerabilities", "-v", "2024-07-01T00:00:00=1.0", "-v", "2024-08-01T00:00:00=2.0"])
    result = cli(["custom-metrics", "get", "-t", "shipping-integrations", "-k", "vulnerabilities"])
    assert result['total'] == 3, "should have total of 3 metrics data points"
    print("There is not a good way to test this today because there is a pre-requisite that the custom metric already exists.")
    print("If you manually create the custom metric named 'vulnerabilities' you can run these tests.")
