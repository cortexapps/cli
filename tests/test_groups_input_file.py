from tests.helpers.utils import *

def test():
    cli(["groups", "add", "-t", "cli-test-service", "-f", "tests/test-groups.json"])

    cli(["groups", "add", "-t", "cli-test-service", "-f", "tests/test-groups.json"])
    response = cli(["groups", "get", "-t", "cli-test-service"])
    assert any(group['tag'] == 'group1' for group in response['groups']), "should find group1 in list of groups"
    assert any(group['tag'] == 'group2' for group in response['groups']), "should find group2 in list of groups"

    cli(["groups", "delete", "-t", "cli-test-service", "-f", "tests/test-groups.json"])
    response = cli(["groups", "get", "-t", "cli-test-service"])

    assert not(any(group['tag'] == 'group1' for group in response['groups'])), "should not find group1 in list of groups"
    assert not(any(group['tag'] == 'group2' for group in response['groups'])), "should not find group2 in list of groups"
