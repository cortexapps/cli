from tests.helpers.utils import *
import pytest

def test():
    # Skip test if API key doesn't have secrets permissions
    # The Secrets API may require special permissions or may not be available in all environments
    try:
        # Try to list secrets first to check if we have permission
        response = cli(["secrets", "list"], return_type=ReturnType.RAW)
        if response.exit_code != 0 and "403" in response.stdout:
            pytest.skip("API key does not have permission to access Secrets API")
    except Exception as e:
        if "403" in str(e) or "Forbidden" in str(e):
            pytest.skip("API key does not have permission to access Secrets API")

    # Create a secret
    response = cli(["secrets", "create", "-f", "data/run-time/secret-create.json"])
    assert response['tag'] == 'cli-test-secret', "Should create secret with tag cli-test-secret"
    assert response['name'] == 'CLI Test Secret', "Should have correct name"

    # List secrets and verify it exists
    response = cli(["secrets", "list"])
    assert any(secret['tag'] == 'cli-test-secret' for secret in response['secrets']), "Should find secret with tag cli-test-secret"

    # Get the secret
    response = cli(["secrets", "get", "-t", "cli-test-secret"])
    assert response['tag'] == 'cli-test-secret', "Should get secret with correct tag"
    assert response['name'] == 'CLI Test Secret', "Should have correct name"

    # Update the secret
    cli(["secrets", "update", "-t", "cli-test-secret", "-f", "data/run-time/secret-update.json"])

    # Verify the update
    response = cli(["secrets", "get", "-t", "cli-test-secret"])
    assert response['name'] == 'Updated CLI Test Secret', "Should have updated name"

    # Delete the secret
    cli(["secrets", "delete", "-t", "cli-test-secret"])

    # Verify deletion by checking list
    response = cli(["secrets", "list"])
    assert not any(secret['tag'] == 'cli-test-secret' for secret in response['secrets']), "Should not find deleted secret"
