"""
Tests for the cortex CLI config file
"""

# These tests are all marked to run in serial order because they make modifications to the 
# cortex config file and/or CORTEX_API_KEY value and would potentially impact other tests
# that are running in parallel (with poetry run pytest -n auto), so they are run separately.

# Additionally, order is VERY IMPORTANT in this file because of the way CORTEX_API key is
# deleted, set to invalid values, etc.  Moving test order could impact the overall success
# of pytest.  Tread carefully here.
from cortexapps_cli.cortex import cli

import io
import os
import pytest
import sys
from string import Template

# Requires user input, so use monkeypatch to set it.
@pytest.fixture(scope="session")
def delete_cortex_api_key():
    if "CORTEX_API_KEY" in os.environ:
        del os.environ['CORTEX_API_KEY']

@pytest.mark.serial
def test_config_file_api_key_quotes(tmp_path):
    cortex_api_key = os.getenv('CORTEX_API_KEY')
    f = tmp_path / "cortex_config_api_key_quotes"
    template = Template("""
        [default]
        api_key = "${cortex_api_key}"
        """)
    content = template.substitute(cortex_api_key=cortex_api_key)
    print(content)
    f.write_text(content)
    cli(["-c", str(f), "teams", "list"])

@pytest.mark.serial
def test_environment_variables(capsys):
    cli(["teams", "list"])
    out, err = capsys.readouterr()
    #print(out)
    print("ERR = " + err)
    assert err.partition('\n')[0] == "WARNING: tenant setting overidden by CORTEX_API_KEY", "Warning should be displayed by default"

    cli(["-q", "teams", "list"])
    out, err = capsys.readouterr()
    assert not(err.partition('\n')[0] == "WARNING: tenant setting overidden by CORTEX_API_KEY"), "Warning should be displayed with -q option"

@pytest.mark.serial
def test_config_file_create(monkeypatch, tmp_path, delete_cortex_api_key):
    with pytest.raises(SystemExit) as excinfo:
        monkeypatch.setattr('sys.stdin', io.StringIO('Y'))
        f = tmp_path / "test-config.txt"
        cli(["-c", str(f), "catalog", "list"])

@pytest.mark.serial
def test_config_file_new(tmp_path, capsys, delete_cortex_api_key):
    f = tmp_path / "cortex_config"
    content = """
        [default]
        api_key = REPLACE_WITH_YOUR_CORTEX_API_KEY
        """
    f.write_text(content)
    with pytest.raises(SystemExit) as excinfo:
        cli(["-c", str(f), "teams", "list"])
        out, err = capsys.readouterr()

@pytest.mark.serial
def test_export(capsys, delete_cortex_api_key):
    cli(["-t", "rich-sandbox", "backup", "export"])
    out, err = capsys.readouterr()
    last_line = out.strip().split("\n")[-1]
    sys.stdout.write(out + "\n\n")
    sys.stdout.write(last_line + "\n\n")
    assert "rich-sandbox" in out 

    export_directory = last_line.replace("Contents available in ", "")
    
    assert len(os.listdir(export_directory + "/catalog")) > 0, "catalog directory has files"
    assert len(os.listdir(export_directory + "/scorecards")) > 0, "scorecards directory has files"
    assert len(os.listdir(export_directory + "/resource-definitions")) > 0, "resource-definitions directory has files"

@pytest.mark.serial
def test_config_file_bad_api_key(tmp_path, capsys, delete_cortex_api_key):
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

@pytest.mark.serial
def test_environment_variable_invalid_key(capsys):
    with pytest.raises(SystemExit) as excinfo:
        os.environ["CORTEX_API_KEY"] = "invalidKey"
        cli(["teams", "list"])
        out, err = capsys.readouterr()
        assert err.partition('\n')[0] == "Unauthorized", "Invalid api key should show Unauthorized message"
