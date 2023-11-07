"""
Tests for backup commands.
"""
from cortexapps_cli.cortex import cli

import pytest
import sys

def test_export():
    cli(["-t", "rich-sandbox", "backup", "export"])

def test_import(capsys):
    # Delete resource definition if it already exists.
    cli(["resource-definitions", "list"])
    out, err = capsys.readouterr()
    if (str(out).find('{"type":"test-resource-definition"') != -1):
        cli(["resource-definitions", "delete", "-t", "test-resource-definition"])
    # Teams created with both teamTag and catalog tag?
    cli(["teams", "list"])
    out, err = capsys.readouterr()
    sys.stdout.write(out)
    if (str(out).find('{"teamTag":"test-team-2"') != -1):
        cli(["catalog", "delete", "-t", "test-team-2"])
    cli(["backup", "import", "-d", "tests/test_backup_export"])

