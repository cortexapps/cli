"""
Tests for plugins commands.
"""
from cortexapps_cli.cortex import cli
import pytest

@pytest.mark.skip(reason="Needs fix for CET-8598")
def test(capsys):
    cli(["plugins", "get"])
    out, err = capsys.readouterr()
    if (str(out).find('{"tag":"my-test-plugin"') != -1):
        cli(["plugins", "delete", "-t", "my-test-plugin"])
    cli(["plugins", "create", "-f", "tests/test_plugins.json"])

    cli(["plugins", "get"])

    cli(["plugins", "update", "-t", "my-test-plugin", "-f", "tests/test_plugins_update.json"])

    cli(["plugins", "get-by-tag", "-t", "my-test-plugin"])

    cli(["plugins", "delete", "-t", "my-test-plugin"])
