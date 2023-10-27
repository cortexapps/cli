"""
Tests for ip-allowlist commands.
"""
from cortexapps_cli.cortex import cli
import requests
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

def test_ip_allowlist_get():
    cli(["ip-allowlist", "get"])

def test_ip_allowlist_validate(tmp_path):
    f = _ip_allowlist_input(tmp_path)
    cli(["ip-allowlist", "validate", "-f", str(f)])

def test_ip_allowlist_replace(tmp_path):
    f = _ip_allowlist_input(tmp_path)
    cli(["ip-allowlist", "replace", "-f", str(f)])

def test_ip_allowlist_empty():
    cli(["ip-allowlist", "replace", "-f", "tests/test_ip_allowlist_empty.json"])
