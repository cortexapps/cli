from tests.helpers.utils import *

# These tests work against jeff-sandbox tenant.
# Need a plan to figure out how we can ensure we have SCIM enabled in an environment to not skip these tests.
def test():
    response = cli(["scim", "list"])
    assert any(user['userName'] == 'jeff.schnitter@proton.me' for user in response['Resources']), "Should find user jeff.schnitter@proton.me"

    response = cli(["scim", "list", "--filter", "userName eq jeff.schnitter@proton.me"])
    assert response['Resources'][0]['userName'] == 'jeff.schnitter@proton.me', "Should find user jeff.schnitter@proton.me"
    id = response['Resources'][0]['id']

    response = cli(["scim", "list", "--filter", "userName eq jeff.schnitter@proton.me", "-a", "name.familyName"])
    assert response['Resources'][0]['name']['familyName'] == 'Schnitter', "Should find family Name"

    response = cli(["scim", "list", "--filter", "userName eq jeff.schnitter@proton.me", "-e", "name.familyName"])
    assert 'familyName' not in response['Resources'][0]['name'].keys(), "Should not have familyName in response"

    response = cli(["scim", "get", "--id", id])
    assert response['id'] == id, "Should find matching id based on query"
