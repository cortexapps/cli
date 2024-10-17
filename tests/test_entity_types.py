from tests.helpers.utils import *

def test_resource_definitions(capsys):
    response = cli(["entity-types", "list"])
    entity_types = response['definitions']
    assert any(definition['type'] == 'api' for definition in entity_types), "Should find entity type named 'api'"

    if any(definition['type'] == 'test-entity-type' for definition in entity_types):
       cli(["entity-types", "delete", "-ty", "test-entity-type"])
#    cli(["entity-types", "create", "-f", "tests/test-resource-definition.json"])
#
#    cli(["entity-types", "list"])
#    assert any(definition['type'] == 'test-entity-type' for definition in response['definitions']), "Should find entity type named 'test-entity-type'"
#
#    cli(["entity-types", "get", "-t", "test-resource-definition"])
#
#    cli(["entity-types", "update", "-t", "test-resource-definition", "-f", "tests/test-resource-definition-update.json"])
