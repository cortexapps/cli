import pytest
from tests.gh_helpers import gh_api, run_workflow, get_env, RESOURCE_PREFIX


@pytest.mark.functional
def test_gh_get_commit(gh_test_repo, gh_default_sha, import_functional_workflows):
    """Test the github.getCommit workflow action block.

    Triggers a Cortex workflow that retrieves a specific commit from the test
    repo using the default branch HEAD SHA. Verifies the workflow run completes
    successfully and the commit exists via the gh API.
    """
    repo = gh_test_repo

    # 1. Trigger the workflow to get the commit
    result = run_workflow(
        tag="func-test-gh-get-commit",
        initial_context={"repo": repo, "commit-sha": gh_default_sha},
    )

    # 2. Verify the Cortex workflow run completed successfully
    status = result.get("status", "").upper()
    assert status == "COMPLETED", (
        f"Workflow run status was '{status}', expected 'COMPLETED'. "
        f"Full response: {result}"
    )

    # 3. Verify GitHub side-effect: the commit exists in the repo
    commit = gh_api("GET", f"/repos/{repo}/commits/{gh_default_sha}")
    assert commit is not None, (
        f"Expected commit '{gh_default_sha}' to exist in repo '{repo}', "
        f"but it was not found."
    )
    assert commit.get("sha") == gh_default_sha, (
        f"Expected commit SHA '{gh_default_sha}', got '{commit.get('sha')}'"
    )


@pytest.mark.functional
def test_gh_list_commits(gh_test_repo, gh_default_sha, import_functional_workflows):
    """Test the github.listCommits workflow action block.

    Triggers a Cortex workflow that lists commits in the test repo, then
    verifies the commits list is non-empty via the gh API.
    """
    repo = gh_test_repo

    # 1. Trigger the workflow to list commits
    result = run_workflow(
        tag="func-test-gh-list-commits",
        initial_context={"repo": repo},
    )

    # 2. Verify the Cortex workflow run completed successfully
    status = result.get("status", "").upper()
    assert status == "COMPLETED", (
        f"Workflow run status was '{status}', expected 'COMPLETED'. "
        f"Full response: {result}"
    )

    # 3. Verify GitHub side-effect: commits list is non-empty
    commits = gh_api("GET", f"/repos/{repo}/commits")
    assert commits is not None and len(commits) > 0, (
        f"Expected to find at least one commit in repo '{repo}', but the list was empty."
    )
