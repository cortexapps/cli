import pytest
from tests.functional.gh_helpers import gh_api, run_workflow


@pytest.mark.functional
def test_gh_branch_protection_lifecycle(gh_test_repo, gh_default_sha, import_functional_workflows):
    """Test branch protection lifecycle: update → get → delete.

    Exercises github.updateBranchProtectionRules,
    github.getBranchProtectionRules, and github.deleteBranchProtectionRules
    workflow action blocks in a single flow.
    """
    repo = gh_test_repo

    # Ensure no existing protection rules
    try:
        gh_api("DELETE", f"/repos/{repo}/branches/main/protection")
    except RuntimeError:
        pass

    try:
        # 1. Update (create) branch protection via workflow
        result = run_workflow(
            tag="func-test-gh-update-branch-protection-rules",
            initial_context={
                "repo": repo,
                "branch": "main",
                "rules": '{"required_status_checks":null,"enforce_admins":true,"required_pull_request_reviews":null,"restrictions":null}',
            },
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"updateBranchProtectionRules workflow failed: {result}"
        )

        # Verify: protection rules exist
        protection = gh_api("GET", f"/repos/{repo}/branches/main/protection")
        assert protection is not None, (
            f"Expected branch protection rules on 'main', but they were not found."
        )

        # 2. Get branch protection via workflow
        result = run_workflow(
            tag="func-test-gh-get-branch-protection-rules",
            initial_context={"repo": repo, "branch": "main"},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"getBranchProtectionRules workflow failed: {result}"
        )

        # 3. Delete branch protection via workflow
        result = run_workflow(
            tag="func-test-gh-delete-branch-protection-rules",
            initial_context={"repo": repo, "branch": "main"},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"deleteBranchProtectionRules workflow failed: {result}"
        )

        # Verify: protection rules no longer exist
        try:
            gh_api("GET", f"/repos/{repo}/branches/main/protection")
            assert False, (
                f"Expected branch protection on 'main' to be deleted, but it still exists."
            )
        except RuntimeError:
            pass  # Expected: protection is gone, GET returns 404
    finally:
        try:
            gh_api("DELETE", f"/repos/{repo}/branches/main/protection")
        except RuntimeError:
            pass
