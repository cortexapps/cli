from tests.helpers.utils import *
"""
Tests for the cortex CLI config file
"""

# These tests are all marked to run in serial order because they make modifications to the 
# cortex config file and/or CORTEX_API_KEY value and would potentially impact other tests
# that are running in parallel (with poetry run pytest -n auto), so they are run separately.

# Additionally, order is VERY IMPORTANT in this file because of the way CORTEX_API key is
# deleted, set to invalid values, etc.  Moving test order could impact the overall success
# of pytest.  Tread carefully here.

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
    f.write_text(content)
    cli(["-c", str(f), "entity-types", "list"])

@pytest.mark.serial
def test_config_file_create(monkeypatch, tmp_path):
    monkeypatch.setattr('sys.stdin', io.StringIO('y'))
    f = tmp_path / "test-config.txt"
    response = cli(["-c", str(f), "-k", os.getenv('CORTEX_API_KEY'), "scorecards", "list"])
    assert any(scorecard['tag'] == 'cli-test-scorecard' for scorecard in response['scorecards']), "Should find scorecard with tag cli-test-scorecard"

@pytest.mark.serial
def test_config_file_bad_api_key(monkeypatch, tmp_path, delete_cortex_api_key):
    monkeypatch.setattr('sys.stdin', io.StringIO('y'))
    f = tmp_path / "test-config-bad-api-key.txt"
    response = cli(["-c", str(f), "-k", "invalidApiKey", "scorecards", "list"], return_type=ReturnType.RAW)
    assert "401 Client Error: Unauthorized" in str(response), "should get Unauthorized error"

@pytest.mark.serial
def test_environment_variable_invalid_key():
    os.environ["CORTEX_API_KEY"] = "invalidKey"
    response = cli(["scorecards", "list"], return_type=ReturnType.RAW)
    assert "401 Client Error: Unauthorized" in str(response), "should get Unauthorized error"
