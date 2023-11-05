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
