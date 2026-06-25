from tests.helpers.utils import *

def test_catalogs_crud():
    """Test full lifecycle: create, list, get, delete for catalogs."""

    # Create a catalog from a JSON file
    cli(["catalogs", "create", "-f", "data/import/catalogs/cli-test-catalog.json"])

    # List catalogs and verify the new one exists
    response = cli(["catalogs", "list"])
    assert any(catalog['slug'] == 'cli-test-catalog' for catalog in response['catalogs']), \
        "Should find catalog with slug cli-test-catalog"

    # Get the specific catalog by slug
    response = cli(["catalogs", "get", "-t", "cli-test-catalog"])
    assert response['name'] == "CLI Test Catalog", "Catalog name should match"
    assert response['slug'] == "cli-test-catalog", "Catalog slug should match"

    # Delete the catalog
    cli(["catalogs", "delete", "-t", "cli-test-catalog"])

    # Verify deletion - get should return 404
    result = cli(["catalogs", "get", "-t", "cli-test-catalog"], ReturnType.RAW)
    assert result.exit_code == 1, "Getting a deleted catalog should fail"
