"""
Tests for version commands.
"""
from cortexapps_cli.cortex import cli
import pytest

def test_version():
    with pytest.raises(SystemExit) as excinfo:
        cli(["-v"])

def test_help():
    with pytest.raises(SystemExit) as excinfo:
        cli(["-h"])

def test_no_parms():
    with pytest.raises(SystemExit) as excinfo:
        cli([])

def test_integrations_no_parms():
    with pytest.raises(SystemExit) as excinfo:
        cli(["integrations"])

def test_integrations_help():
    with pytest.raises(SystemExit) as excinfo:
        cli(["integrations", "-h"])

def test_integrations_command():
    with pytest.raises(SystemExit) as excinfo:
        cli(["integrations", "aws"])

def test_command_no_options():
    with pytest.raises(SystemExit) as excinfo:
        cli(["catalog"])

def test_new_config_file(tmp_path):
    f = tmp_path / "cortex_config"
    content = """
        [default]
        api_key = REPLACE_WITH_YOUR_CORTEX_API_KEY
        """
    f.write_text(content)
    with pytest.raises(SystemExit) as excinfo:
        cli(["-c", str(f), "catalog", "list"])
