from tests.helpers.utils import *

def test_groups():
    cli(["groups", "add", "-t", "test-service", "-g", "test-group-2,test-group-3"])
    response = cli(["groups", "get", "-t", "test-service"])
    assert any(group['tag'] == 'test-group-2' for group in response['groups']), "Should find group named test-group-2 in entity test-service"

    cli(["groups", "delete", "-t", "test-service", "-g", "test-group-2,test-group-3"])
    response = cli(["groups", "get", "-t", "test-service"])
    assert not(any(group['tag'] == 'test-group-2' for group in response['groups'])), "After delete, should not find group named test-group-2 in entity test-service"
