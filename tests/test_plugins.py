"""
Tests for plugins commands.
"""
from cortexapps_cli.cortex import cli

def test_plugins_create(capsys):
    cli(["plugins", "get"])
    out, err = capsys.readouterr()
    if (str(out).find('{"tag":"my-test-plugin"') != -1):
        cli(["plugins", "delete", "-t", "my-test-plugin"])
    cli(["plugins", "create", "-f", "tests/test_plugins.json"])

    cli(["plugins", "get"])

    cli(["plugins", "update", "-t", "my-test-plugin", "-f", "tests/test_plugins_update.json"])

    cli(["plugins", "get-by-tag", "-t", "my-test-plugin"])

    cli(["plugins", "delete", "-t", "my-test-plugin"])
