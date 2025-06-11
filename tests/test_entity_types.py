from tests.helpers.utils import *

def test_resource_definitions(capsys):
    response = cli(["entity-types", "list"])
    entity_types = response['definitions']
    assert any(definition['type'] == 'cli-test' for definition in entity_types), "Should find entity type named 'cli-test'"

    if any(definition['type'] == 'cli-test' for definition in entity_types):
       cli(["entity-types", "delete", "-t", "cli-test"])
    cli(["entity-types", "create", "-f", "data/import/entity-types/cli-test.json"])

    response = cli(["entity-types", "list"])
    assert any(definition['type'] == 'cli-test' for definition in response['definitions']), "Should find entity type named 'cli-test'"

    cli(["entity-types", "get", "-t", "cli-test"])

    cli(["entity-types", "update", "-t", "cli-test", "-f", "data/run-time/entity-type-update.json"])
