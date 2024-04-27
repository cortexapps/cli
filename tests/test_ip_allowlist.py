"""
Tests for ip-allowlist commands.
"""
from cortexapps_cli.cortex import cli
import requests
import pytest
from string import Template

def _ip_allowlist_input(tmp_path):
    ip_address = requests.get("https://ip.me").text.strip()
    f = tmp_path / "test_ip_allowlist_input.json"
    template = Template("""
        {
          "entries": [
            {
              "address": "${ip_address}",
              "description": "string"
            }
          ]
        }
        """)
    content = template.substitute(ip_address=ip_address)
    f.write_text(content)
    return f

def test(capsys, tmp_path):
    cli(["ip-allowlist", "get"])

    f = _ip_allowlist_input(tmp_path)
    cli(["ip-allowlist", "validate", "-f", str(f)])

    f = _ip_allowlist_input(tmp_path)
    cli(["ip-allowlist", "replace", "-f", str(f)])

    cli(["ip-allowlist", "replace", "-f", "tests/test_ip_allowlist_empty.json"])

    with pytest.raises(SystemExit) as excinfo:
        cli(["ip-allowlist", "validate", "-f", "tests/test_ip_allowlist_invalid.json"])
        out, err = capsys.readouterr()
        response = json.loads(out)
        #print(err)
        #assert err.partition('\n')[0] == "Unauthorized", "Invalid api key should show Unauthorized message"
        assert out == "Bad Request"
        assert excinfo.value.code == 400
