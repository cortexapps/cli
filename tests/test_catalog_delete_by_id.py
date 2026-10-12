from tests.helpers.utils import *

def test():
    # Create an entity
    cli(["catalog", "create", "-f", "data/run-time/catalog-delete-by-id-entity.yaml"])

    # Get its CID
    response = cli(["catalog", "details", "-t", "cli-test-delete-by-id-entity"])
    cid = response['id']
    assert cid.startswith("en"), f"Expected a CID starting with 'en', got: {cid}"

    # Delete by CID
    cli(["catalog", "delete-by-id", "--id", cid])

    # Verify it's gone
    response = cli(["catalog", "details", "-t", "cli-test-delete-by-id-entity"], ReturnType.RAW)
    assert "HTTP Error 404:" in response.stdout, "Entity should be deleted (404 expected)"
