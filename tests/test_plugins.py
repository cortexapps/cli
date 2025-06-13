from tests.helpers.utils import *

def test():
    response = cli(["plugins", "list"])

    if any(plugin['tag'] == 'cli-test-plugin' for plugin in response['plugins']):
        cli(["plugins", "delete", "-t", "cli-test-plugin"])

    cli(["plugins", "create", "-f", "data/import/plugins/cli-test-plugin.json"])
    response = cli(["plugins", "list"])
    assert any(plugin['tag'] == 'cli-test-plugin' for plugin in response['plugins']), "Plugin named cli-test-plugin should be in list of plugins"

    cli(["plugins", "replace", "-t", "cli-test-plugin", "-f", "tests/test_plugins_update.json"])
    response = cli(["plugins", "get", "-t", "cli-test-plugin"])
    assert response['tag'] == "cli-test-plugin", "Plugin named cli-test-plugin should be returned by get"

    cli(["plugins", "delete", "-t", "cli-test-plugin"])
    response = cli(["plugins", "list"])
    assert not(any(plugin['tag'] == 'cli-test-plugin' for plugin in response['plugins'])), "Plugin named cli-test-plugin should have been deleted"
