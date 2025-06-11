from tests.helpers.utils import *
from urllib.error import HTTPError
import pytest

def test():
    response = cli(["scim", "list"], ReturnType.STDOUT)

    if "HTTP Error 403" in response:
        print("SCIM not set up or API key does not have permissions, not running test.")
        print("API should probably return something other than a 403 when SCIM isn't set up")
        print("because it's not possible to determine if this is a setup or permissions issue.")
    else:
        response = cli(["scim", "list"])
        total_results = response['totalResults']
        assert total_results >= 0, "Total results should be returned as an integer"
        print("total results = " + str(total_results))

        if total_results > 0:
            assert any(user['userName'] == 'jeff.schnitter@proton.me' for user in response['Resources']), "Should find user jeff.schnitter@proton.me"

            response = cli(["scim", "list", "--filter", "userName eq jeff.schnitter@proton.me"])
            assert response['Resources'][0]['userName'] == 'jeff.schnitter@proton.me', "Should find user jeff.schnitter@proton.me"
            id = response['Resources'][0]['id']

            response = cli(["scim", "list", "--filter", "userName eq jeff.schnitter@proton.me", "-a", "name.familyName"])
            assert 'familyName' in response['Resources'][0]['name'].keys(), "Should find familyName in response"

            response = cli(["scim", "list", "--filter", "userName eq jeff.schnitter@proton.me", "-e", "name.familyName"])
            assert 'familyName' not in response['Resources'][0]['name'].keys(), "Should not have familyName in response"

            response = cli(["scim", "get", "--id", id])
            assert response['id'] == id, "Should find matching id based on query"
        else:
            print("Not running any scim tests, which is lucky because I have not thought of a good way to make these tests generic.")
