from common import *

@pytest.mark.skipif(allow_team_entities_in_catalog_api() == False, reason="Account flag ALLOW_TEAM_ENTITIES_IN_CATALOG_API is not set")
def test(capsys):
    # without increased page size to ensure all entities are returned, test is flaky because API by default only returns
    # 50 entities per page and the content of the entities in page 0 seems to be somewhat random
    response = cli_command(capsys, ["catalog", "list", "-g", "public-api-test", "-z", "5000", "-io", "-in", "team:members"])
    list = [entity for entity in response['entities'] if entity['tag'] == "search-experience"]
    assert not list == None, "found search-experience entity in response"
    assert len(list[0]['members']) > 0, "response has non-empty array of members"
