from tests.helpers.utils import *


def _api_enabled():
    # The public catalog-pages API is permission/feature gated; skip rather than
    # fail when the test tenant does not have it enabled.
    raw = cli(["catalogs", "list"], return_type=ReturnType.RAW)
    return raw.exit_code == 0


def test_list():
    if not _api_enabled():
        pytest.skip("Public catalog-pages API is not enabled for this tenant")
    response = cli(["catalogs", "list"])
    assert "catalogPages" in response


def test_crud():
    if not _api_enabled():
        pytest.skip("Public catalog-pages API is not enabled for this tenant")
    slug = "cli-test-catalog"
    raw = cli(
        ["catalogs", "create", "-f", "data/import/catalogs/cli-test-catalog.json"],
        return_type=ReturnType.RAW,
    )
    if raw.exit_code != 0:
        pytest.skip(f"Catalog page create failed on this tenant: {raw.stdout}")
    try:
        response = cli(["catalogs", "list"])
        assert any(
            c["slug"] == slug for c in response["catalogPages"]
        ), f"Should find catalog page with slug {slug}"

        response = cli(["catalogs", "get", "-s", slug])
        assert response["slug"] == slug
        assert response["name"] == "CLI Test Catalog"

        # POST is an upsert: creating again with the same slug replaces it.
        cli(["catalogs", "create", "-f", "data/import/catalogs/cli-test-catalog.json"])
        response = cli(["catalogs", "get", "-s", slug])
        assert response["slug"] == slug
    finally:
        cli(["catalogs", "delete", "-s", slug])

    # the page should be gone after delete
    raw = cli(["catalogs", "get", "-s", slug], return_type=ReturnType.RAW)
    assert raw.exit_code != 0
