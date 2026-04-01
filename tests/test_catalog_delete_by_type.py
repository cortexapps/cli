from tests.helpers.utils import *

@pytest.mark.skip(reason="Disabled until CET-24425 is resolved.")
def test():
    # Create the entity type
    cli(["entity-types", "create", "-f", "data/run-time/entity-type-delete-by-type.json"], ReturnType.RAW)

    # Create an entity of that type
    cli(["catalog", "create", "-f", "data/run-time/catalog-delete-by-type-entity.yaml"])

    # Verify the entity exists
    response = cli(["catalog", "list", "-t", "cli-test-delete-by-type"])
    assert response['total'] > 0, "Should find at least 1 entity of type 'cli-test-delete-by-type'"

    # Delete all entities of that type
    cli(["catalog", "delete-by-type", "-t", "cli-test-delete-by-type"])

    # Verify 0 entities remain of that type
    response = cli(["catalog", "list", "-t", "cli-test-delete-by-type"])
    assert response['total'] == 0, f"Expected 0 entities of x-cortex-type:cli-test-delete-by-type, but found: {response['total']}"
