"""
Tests for backup commands.
"""
from cortexapps_cli.cortex import cli

import pytest
import sys

def test_import(capsys):
    cli(["backup", "import", "-d", "tests/test_backup_export"])

