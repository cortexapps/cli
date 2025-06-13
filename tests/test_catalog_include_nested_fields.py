from tests.helpers.utils import *

def test():
    response = cli(["catalog", "list", "-t", "team"], ReturnType.STDOUT)

    if "HTTP Error 400: Bad Request - Cannot request teams." in response:
        print("This test requires feature flag ALLOW_TEAM_ENTITIES_IN_CATALOG_API, which does not appear to be set, so not running test.")
        print("This flag will eventually be set for all workspaces and this check can be removed.  However, as of June 2025 this has not been done.")
        return

    response = cli(["catalog", "list", "-g", "cli-test", "-io", "-in", "team:members"])
    list = [entity for entity in response['entities'] if entity['tag'] == "cli-test-team-1"]
    assert not list == None, "found an entity in response"
    assert len(list[0]['members']) > 0, "response has non-empty array of members"
