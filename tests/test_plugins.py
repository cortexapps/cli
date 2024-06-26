from common import *

def test(capsys):
    pluginTag = "public-api-test-plugin"

    response = cli_command(capsys, ["plugins", "get"])
    if any(plugin['tag'] == pluginTag for plugin in response['plugins']):
        cli(["plugins", "delete", "-t", pluginTag])

    cli_command(capsys, ["plugins", "create", "-f", "data/run-time/test_plugins.json"])

    response = cli_command(capsys, ["plugins", "get"])
    assert any(plugin['tag'] == pluginTag for plugin in response['plugins']), "Plugin " + plugin + " returned in get"

    cli_command(capsys, ["plugins", "update", "-t", pluginTag, "-f", "data/run-time//test_plugins_update.json"])

    response = cli_command(capsys, ["plugins", "get-by-tag", "-t", pluginTag])
    assert response['tag'] == pluginTag, "Plugin " + plugin + " returned by get-by-tag"
    assert response['description'] == "Just testing plugin updates", "Plugin " + plugin + " description updated"

    cli(["-q", "plugins", "delete", "-t", pluginTag])
    response = cli_command(capsys, ["plugins", "get"])
    assert not any(plugin['tag'] == pluginTag for plugin in response['plugins']), "Plugin " + plugin + " returned in get"
