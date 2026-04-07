import pytest
from tests.functional.gh_helpers import gh_api, run_workflow


@pytest.mark.functional
def test_gh_list_branches(gh_test_repo, gh_default_sha, import_functional_workflows):
    """Test the github.listBranches workflow action block.

    Triggers a Cortex workflow that calls GitHub's list-branches API,
    then verifies the response via the gh CLI.
    """
    # 1. Trigger the workflow
    result = run_workflow(
        tag="func-test-gh-list-branches",
        initial_context={"repo": gh_test_repo},
    )

    # 2. Verify the Cortex workflow run completed successfully
    status = result.get("status", "").upper()
    assert status == "COMPLETED", (
        f"Workflow run status was '{status}', expected 'COMPLETED'. "
        f"Full response: {result}"
    )

    # 3. Verify GitHub side-effect: branches exist on the repo
    branches = gh_api("GET", f"/repos/{gh_test_repo}/branches")
    branch_names = [b["name"] for b in branches]
    assert "main" in branch_names, (
        f"Expected 'main' branch in repo {gh_test_repo}, got: {branch_names}"
    )
