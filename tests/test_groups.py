from tests.helpers.utils import *

def test_groups():
    cli(["groups", "add", "-t", "cli-test-service", "-g", "test-group-2,test-group-3"])
    response = cli(["groups", "get", "-t", "cli-test-service"])
    assert any(group['tag'] == 'test-group-2' for group in response['groups']), "Should find group named test-group-2 in entity cli-test-service"

    cli(["groups", "delete", "-t", "cli-test-service", "-g", "test-group-2,test-group-3"])
    response = cli(["groups", "get", "-t", "cli-test-service"])
    assert not(any(group['tag'] == 'test-group-2' for group in response['groups'])), "After delete, should not find group named test-group-2 in entity cli-test-service"
