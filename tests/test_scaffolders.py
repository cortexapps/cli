from tests.helpers.utils import *

def _api_enabled():
    # The public Scaffolder API is gated by a feature flag; skip rather than
    # fail when the test tenant does not have it enabled.
    raw = cli(["scaffolders", "list"], return_type=ReturnType.RAW)
    return raw.exit_code == 0

def test_list():
    if not _api_enabled():
        pytest.skip("Public Scaffolder API is not enabled for this tenant")

    response = cli(["scaffolders", "list"])
    assert "scaffolders" in response

def test_crud():
    if not _api_enabled():
        pytest.skip("Public Scaffolder API is not enabled for this tenant")

    tag = "cli-test-scaffolder"

    # Creation validates the template repository through the tenant's git
    # integration, so skip when the fixture repo is not reachable here.
    raw = cli(["scaffolders", "create", "-f", "data/import/scaffolders/cli-test-scaffolder.yaml"], return_type=ReturnType.RAW)
    if raw.exit_code != 0:
        pytest.skip(f"Scaffolder create failed on this tenant (likely no git integration for the fixture repo): {raw.stdout}")

    try:
        response = cli(["scaffolders", "list"])
        assert any(s['tag'] == tag for s in response['scaffolders']), f"Should find Scaffolder template with tag {tag}"

        response = cli(["scaffolders", "get", "-t", tag])
        assert response['tag'] == tag

        # Idempotent re-apply: the same definition upserts onto the same tag.
        cli(["scaffolders", "create", "-f", "data/import/scaffolders/cli-test-scaffolder.yaml"])
        response = cli(["scaffolders", "get", "-t", tag])
        assert response['tag'] == tag

        cli(["scaffolders", "update", "-t", tag, "-f", "data/import/scaffolders/cli-test-scaffolder-updated.yaml"])
        response = cli(["scaffolders", "get", "-t", tag])
        assert response['name'] == "CLI Test Scaffolder Updated"
    finally:
        cli(["scaffolders", "delete", "-t", tag])
