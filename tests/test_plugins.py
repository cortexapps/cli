"""
Tests for plugins commands.
"""
from cortexapps_cli.cortex import cli

import json

def _plugins_get(capsys):
    cli(["plugins", "get"])
    out, err = capsys.readouterr()
    json_data = json.loads(out)

    return json_data

def test_plugins(capsys):
    json_data = _plugins_get(capsys)

    if any(entity['tag'] == 'test-plugins' for entity in json_data['plugins']):
        cli(["plugins", "delete", "-t", "test-plugins"])
    cli(["plugins", "create", "-f", "tests/test_plugins.json"])
    cli(["plugins", "update", "-t", "test-plugins", "-f", "tests/test_plugins_update.json"])
    cli(["plugins", "get-by-tag", "-t", "test-plugins"])
    cli(["plugins", "delete", "-t", "test-plugins"])
