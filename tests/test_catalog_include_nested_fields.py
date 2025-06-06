from tests.helpers.utils import *

def test():
    response = cli(["catalog", "create", "-f", "data/run-time/test-team-1.yaml"])

    response = cli(["catalog", "list", "-g", "cli-test", "-io", "-in", "team:members"])
    list = [entity for entity in response['entities'] if entity['tag'] == "test-team-1"]
    assert not list == None, "found an entity in response"
    assert len(list[0]['members']) > 0, "response has non-empty array of members"
