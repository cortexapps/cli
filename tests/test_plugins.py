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

def test_plugins_get():
    cli(["plugins", "get"])

def test_plugins_update():
    cli(["plugins", "update", "-t", "my-test-plugin", "-f", "tests/test_plugins_update.json"])

def test_plugins_get_by_tag():
    cli(["plugins", "get-by-tag", "-t", "my-test-plugin"])

def test_plugins_delete():
    cli(["plugins", "delete", "-t", "my-test-plugin"])
