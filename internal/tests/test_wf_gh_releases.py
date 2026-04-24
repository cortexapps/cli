import pytest
from tests.gh_helpers import gh_api, run_workflow


@pytest.mark.functional
def test_gh_release_lifecycle(gh_test_repo, gh_default_sha, import_functional_workflows):
    """Test release lifecycle: create → get by tag → list.

    Exercises github.createRelease, github.getReleaseByTag, and
    github.listReleases workflow action blocks in a single flow.
    """
    repo = gh_test_repo
    tag_name = "cli-functional-test-v1.0.0"

    try:
        gh_api("DELETE", f"/repos/{repo}/git/refs/tags/{tag_name}")
    except RuntimeError:
        pass

    # Create a lightweight tag as a precondition
    gh_api("POST", f"/repos/{repo}/git/refs", input_data={
        "ref": f"refs/tags/{tag_name}",
        "sha": gh_default_sha,
    })

    release_id = None
    try:
        # 1. Create release via workflow
        result = run_workflow(
            tag="func-test-gh-create-release",
            initial_context={"repo": repo, "tag-name": tag_name},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"createRelease workflow failed: {result}"
        )

        # Verify: release exists
        release = gh_api("GET", f"/repos/{repo}/releases/tags/{tag_name}")
        assert release is not None, (
            f"Expected release for tag '{tag_name}' to exist, but it was not found."
        )
        release_id = release.get("id")

        # 2. Get release by tag via workflow
        result = run_workflow(
            tag="func-test-gh-get-release-by-tag",
            initial_context={"repo": repo, "tag": tag_name},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"getReleaseByTag workflow failed: {result}"
        )

        # 3. List releases via workflow
        result = run_workflow(
            tag="func-test-gh-list-releases",
            initial_context={"repo": repo},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"listReleases workflow failed: {result}"
        )
    finally:
        if release_id is not None:
            try:
                gh_api("DELETE", f"/repos/{repo}/releases/{release_id}")
            except RuntimeError:
                pass
        try:
            gh_api("DELETE", f"/repos/{repo}/git/refs/tags/{tag_name}")
        except RuntimeError:
            pass
