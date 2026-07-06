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
    response = cli(["catalogs", "get", "-s", "cli-test-catalog"])
    assert response['name'] == "CLI Test Catalog", "Catalog name should match"
    assert response['slug'] == "cli-test-catalog", "Catalog slug should match"

    # Delete the catalog
    cli(["catalogs", "delete", "-s", "cli-test-catalog"])

    # Verify deletion - get should return 404
    result = cli(["catalogs", "get", "-s", "cli-test-catalog"], ReturnType.RAW)
    assert result.exit_code == 1, "Getting a deleted catalog should fail"


def test_catalogs_upsert_replaces_existing():
    """UPSERT mode (default) should replace an existing catalog without error."""

    cli(["catalogs", "create", "-f", "data/import/catalogs/cli-test-catalog.json"])

    try:
        # Second create with same slug should succeed (upsert replaces)
        response = cli(["catalogs", "create", "-f", "data/import/catalogs/cli-test-catalog.json"])
        assert response['slug'] == 'cli-test-catalog', "Upserted catalog should be returned"
    finally:
        cli(["catalogs", "delete", "-s", "cli-test-catalog"])


def test_catalogs_create_mode_fails_on_duplicate():
    """mode=CREATE should fail with an error if the slug already exists."""

    cli(["catalogs", "create", "-f", "data/import/catalogs/cli-test-catalog.json"])

    try:
        result = cli(
            ["catalogs", "create", "-f", "data/import/catalogs/cli-test-catalog.json", "--mode", "CREATE"],
            ReturnType.RAW,
        )
        assert result.exit_code == 1, "CREATE mode should fail if slug already exists"
    finally:
        cli(["catalogs", "delete", "-s", "cli-test-catalog"])
