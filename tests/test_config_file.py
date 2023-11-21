"""
Tests for the cortex CLI config file
"""
from cortexapps_cli.cortex import cli

import io
import os
import pytest
import sys
from string import Template

# Requires user input, so use monkeypatch to set it.
def test_config_file_create(monkeypatch, tmp_path):
    with pytest.raises(SystemExit) as excinfo:
        monkeypatch.setattr('sys.stdin', io.StringIO('Y'))
        f = tmp_path / "test-config.txt"
        cli(["-c", str(f), "catalog", "list"])

def test_config_file_new(tmp_path, capsys):
    f = tmp_path / "cortex_config"
    content = """
        [default]
        api_key = REPLACE_WITH_YOUR_CORTEX_API_KEY
        """
    f.write_text(content)
    with pytest.raises(SystemExit) as excinfo:
        cli(["-c", str(f), "teams", "list"])
        out, err = capsys.readouterr()

def test_config_file_api_key_quotes(tmp_path):
    cortex_api_key = os.getenv('CORTEX_API_KEY')
    f = tmp_path / "cortex_config_api_key_quotes"
    template = Template("""
        [default]
        api_key = "${cortex_api_key}"
        """)
    content = template.substitute(cortex_api_key=cortex_api_key)
    f.write_text(content)
    cli(["-c", str(f), "teams", "list"])

def test_config_file_bad_api_key(tmp_path, capsys):
    f = tmp_path / "cortex_config_bad_api_key"
    content = """
        [default]
        api_key = invalidApiKey
        """
    f.write_text(content)
    with pytest.raises(SystemExit) as excinfo:
        cli(["-c", str(f), "teams", "list"])
        out, err = capsys.readouterr()
        assert err.partition('\n')[0] == "Unauthorized", "Invalid api key should show Unauthorized message"
