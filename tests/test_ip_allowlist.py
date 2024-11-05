from tests.helpers.utils import *
import requests

def test(capsys, tmp_path):
    ip_address = requests.get("https://ip.me").text.strip()
    ip_param = ip_address + ":My current IP"
    cli(["ip-allowlist", "validate", "-a", ip_param])
    cli(["ip-allowlist", "replace", "-a", ip_param])

    response = cli(["ip-allowlist", "get"])
    assert response['entries'][0]['address'] == ip_address, "Should have a single IP address in allowlist"

    cli(["ip-allowlist", "remove-all"])
    response = cli(["ip-allowlist", "get"])
    assert len(response['entries']) == 0, "Should not have any entries in allowlist"
