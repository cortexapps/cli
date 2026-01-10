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

    # Verify iconTag was set correctly
    response = cli(["entity-types", "get", "-t", "cli-test"])
    assert response.get('iconTag') == "Cortex-builtin::Basketball", "iconTag should be set to Cortex-builtin::Basketball"

    cli(["entity-types", "update", "-t", "cli-test", "-f", "data/run-time/entity-type-update.json"])


def test_resource_definitions_invalid_icon():
    # API does not reject invalid iconTag values - it uses a default icon instead
    # This test verifies that behavior and will catch if the API changes to reject invalid icons
    response = cli(["entity-types", "create", "-f", "data/run-time/entity-type-invalid-icon.json"], return_type=ReturnType.RAW)
    assert response.exit_code == 0, "Creation should succeed even with invalid iconTag (API uses default icon)"

    # Clean up the test entity type
    cli(["entity-types", "delete", "-t", "cli-test-invalid-icon"])
