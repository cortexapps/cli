from tests.helpers.utils import *

def test():
    cli(["catalog", "create", "-f", "data/run-time/test-service.yaml"])
    cli(["groups", "add", "-t", "test-service", "-f", "tests/test-groups.json"])

    cli(["groups", "add", "-t", "test-service", "-f", "tests/test-groups.json"])
    response = cli(["groups", "get", "-t", "test-service"])
    assert any(group['tag'] == 'group1' for group in response['groups']), "should find group1 in list of groups"
    assert any(group['tag'] == 'group2' for group in response['groups']), "should find group2 in list of groups"

    cli(["groups", "delete", "-t", "test-service", "-f", "tests/test-groups.json"])
    response = cli(["groups", "get", "-t", "test-service"])

    assert not(any(group['tag'] == 'group1' for group in response['groups'])), "should not find group1 in list of groups"
    assert not(any(group['tag'] == 'group2' for group in response['groups'])), "should not find group2 in list of groups"
