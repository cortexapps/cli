from tests.helpers.utils import *
"""
Tests for the cortex CLI config file
"""

import io
import os
import pytest
import sys
from string import Template

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

def test_config_file_create(monkeypatch, tmp_path):
    monkeypatch.setattr('sys.stdin', io.StringIO('y'))
    f = tmp_path / "test-config.txt"
    response = cli(["-c", str(f), "-k", os.getenv('CORTEX_API_KEY'), "scorecards", "list"])
    assert any(scorecard['tag'] == 'cli-test-scorecard' for scorecard in response['scorecards']), "Should find scorecard with tag cli-test-scorecard"

def test_config_file_bad_api_key(monkeypatch, tmp_path):
    monkeypatch.delenv("CORTEX_API_KEY")
    monkeypatch.setattr('sys.stdin', io.StringIO('y'))
    f = tmp_path / "test-config-bad-api-key.txt"
    response = cli(["-c", str(f), "-k", "invalidApiKey", "scorecards", "list"], return_type=ReturnType.RAW)
    assert "401 Client Error: Unauthorized" in str(response), "should get Unauthorized error"

def test_environment_variable_invalid_key(monkeypatch):
    monkeypatch.setenv("CORTEX_API_KEY", "invalidKey")
    response = cli(["scorecards", "list"], return_type=ReturnType.RAW)
    assert "401 Client Error: Unauthorized" in str(response), "should get Unauthorized error"

def test_config_file_bad_url(monkeypatch, tmp_path):
    monkeypatch.delenv("CORTEX_BASE_URL")
    cortex_api_key = os.getenv('CORTEX_API_KEY')
    f = tmp_path / "cortex_config_api_key_quotes"
    template = Template("""
        [default]
        api_key = "${cortex_api_key}"

        [mySection]
        api_key = "${cortex_api_key}"
        base_url = https://bogus.url
        """)
    content = template.substitute(cortex_api_key=cortex_api_key)
    f.write_text(content)
    response =  cli(["-c", str(f), "-l", "DEBUG", "-t", "mySection", "entity-types", "list"], return_type=ReturnType.RAW)
    assert "Max retries exceeded with url" in str(response), "should get max retries error"

def test_config_file_base_url_env_var(monkeypatch, tmp_path):
    cortex_api_key = os.getenv('CORTEX_API_KEY')
    f = tmp_path / "cortex_config_api_key_quotes"
    template = Template("""
        [default]
        api_key = "${cortex_api_key}"

        [mySection]
        api_key = "${cortex_api_key}"
        base_url = https://bogus.url
        """)
    content = template.substitute(cortex_api_key=cortex_api_key)
    f.write_text(content)
    monkeypatch.setenv("CORTEX_BASE_URL", "https://api.getcortexapp.com")
    cli(["-c", str(f), "-t", "mySection", "entity-types", "list"])
