from tests.helpers.utils import *

def test():
    response = cli(["plugins", "list"])

    if any(plugin['tag'] == 'my-test-plugin' for plugin in response['plugins']):
        cli(["plugins", "delete", "-t", "my-test-plugin"])

    cli(["plugins", "create", "-f", "tests/test_plugins.json"])
    response = cli(["plugins", "list"])
    assert any(plugin['tag'] == 'my-test-plugin' for plugin in response['plugins']), "Plugin named my-test-plugin should be in list of plugins"

    cli(["plugins", "replace", "-t", "my-test-plugin", "-f", "tests/test_plugins_update.json"])
    response = cli(["plugins", "get", "-t", "my-test-plugin"])
    assert response['tag'] == "my-test-plugin", "Plugin named my-test-plugin should be returned by get"

    cli(["plugins", "delete", "-t", "my-test-plugin"])
    response = cli(["plugins", "list"])
    assert not(any(plugin['tag'] == 'my-test-plugin' for plugin in response['plugins'])), "Plugin named my-test-plugin should have been deleted"
