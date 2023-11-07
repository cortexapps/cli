"""
Tests for the cortex CLI config file
"""
from cortexapps_cli.cortex import cli

import io
import pytest
import sys

# Requires user input, so use monkeypatch to set it.
def test_create_config_file(monkeypatch, tmp_path):
    with pytest.raises(SystemExit) as excinfo:
        monkeypatch.setattr('sys.stdin', io.StringIO('Y'))
        f = tmp_path / "test-config.txt"
        cli(["-c", str(f), "catalog", "list"])
