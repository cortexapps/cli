from tests.helpers.utils import *

def test():
    cli(["api-keys", "create", "-d", "Key created from CLI test", "-n", "CLI Test Key", "-dr", "USER"])

    response = cli(["api-keys", "list"])
    assert any(key['description'] == 'Key created from CLI test' for key in response['apiKeys']), "Should find key with description 'Key created from CLI test'"

    cid = [key['cid'] for key in response['apiKeys'] if key['description'] == 'Key created from CLI test'][0]
    print("cid = " + cid)
    response = cli(["api-keys", "get", "-c", cid])
    cli(["api-keys", "update", "-c", cid, "-n", "My new name", "-d", "Update: Key created from CLI test"])
    cli(["api-keys", "delete", "-c", cid])
