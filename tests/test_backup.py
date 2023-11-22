"""
Tests for backup commands.
"""
from cortexapps_cli.cortex import cli

import pytest
import sys

def test_export(capsys):
    cli(["-t", "rich-sandbox", "backup", "export"])
    out, err = capsys.readouterr()
    last_line = out.strip().split("\n")[-1]
    sys.stdout.write(out + "\n\n")
    sys.stdout.write(last_line + "\n\n")
    assert "rich-sandbox" in out 

def test_import(capsys):
    cli(["backup", "import", "-d", "tests/test_backup_export"])

