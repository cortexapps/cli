from tests.helpers.utils import *

def test_resource_definitions(capsys):
    cli(["entity-types", "create", "-f", "data/run-time/create-entity-type-empty-schema.json"])

    response = cli(["entity-types", "list"])
    entity_types = response['definitions']
    assert any(definition['type'] == 'cli-test-empty-schema' for definition in entity_types), "Should find entity type named 'cli-test-empty-schema'"

    if any(definition['type'] == 'cli-test-empty-schema' for definition in entity_types):
       cli(["entity-types", "delete", "-t", "cli-test-empty-schema"])
    cli(["entity-types", "create", "-f", "data/run-time/create-entity-type-empty-schema.json"])

    response = cli(["entity-types", "list"])
    assert any(definition['type'] == 'cli-test-empty-schema' for definition in response['definitions']), "Should find entity type named 'cli-test-empty-schema'"

    cli(["entity-types", "get", "-t", "cli-test-empty-schema"])

    cli(["entity-types", "update", "-t", "cli-test-empty-schema", "-f", "data/run-time/update-entity-type-empty-schema.json"])
