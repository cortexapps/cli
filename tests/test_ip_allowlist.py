from common import *

def _ip_allowlist_input(tmp_path, ip_address, description):
    f = tmp_path / "test_ip_allowlist_input.json"
    template = Template("""
        {
          "entries": [
            {
              "address": "${ip_address}",
              "description": "string"
            },
            {
              "address": "127.0.0.1",
              "description": "${description}"
            }
          ]
        }
        """)
    content = template.substitute(ip_address=ip_address, description=description)
    f.write_text(content)
    return f

def test(tmp_path, capsys):
    ip_address = requests.get("https://ip.me").text.strip()

    description = "initial description"
    f = _ip_allowlist_input(tmp_path, ip_address, description)
    response = cli_command(capsys, ["ip-allowlist", "validate", "-f", str(f)])

    # Initial replace
    cli_command(capsys, ["ip-allowlist", "replace", "-f", str(f)])
    response = cli_command(capsys, ["ip-allowlist", "get"])
    assert any(entry['description'] == description for entry in response['entries']), "Allowlist entry should have expected description"

    # Updated replace
    updated_description = "updated description"
    f = _ip_allowlist_input(tmp_path, ip_address, updated_description)
    cli_command(capsys, ["ip-allowlist", "replace", "-f", str(f)])
    response = cli_command(capsys, ["ip-allowlist", "get"])
    assert any(entry['description'] == updated_description for entry in response['entries']), "Allowlist entry should be updated"

    cli_command(capsys, ["ip-allowlist", "replace", "-f", "data/run-time/ip_allowlist_empty.json"])

    with pytest.raises(SystemExit) as excinfo:
       cli(["-q", "catalog", "ip-allowlist", "-f", "data/run-time/ip_allowlist_invalid.json"])
       out, err = capsys.readouterr()

       assert out == "Not Found"
       assert excinfo.value.code == 404
