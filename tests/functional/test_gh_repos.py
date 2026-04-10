import pytest
from tests.functional.gh_helpers import gh_api, run_workflow, safe_delete_repo, get_env, RESOURCE_PREFIX


@pytest.mark.functional
def test_gh_create_repository(gh_test_repo, gh_default_sha, import_functional_workflows):
    """Test the github.createRepository workflow action block.

    Triggers a Cortex workflow that creates a new GitHub repository, then
    verifies the repo exists via the gh API. Sets a custom property on the
    repo after creation for safety tracking. Cleans up afterward.
    """
    org = gh_test_repo.split("/")[0]
    repo_name = "cli-functional-test-create-repo"
    full_repo = f"{org}/{repo_name}"

    # Ensure the repo does not exist before the test
    try:
        safe_delete_repo(full_repo)
    except RuntimeError:
        pass

    try:
        # 1. Trigger the workflow to create the repository
        result = run_workflow(
            tag="func-test-gh-create-repository",
            initial_context={"org": org, "repo-name": repo_name},
        )

        # 2. Verify the Cortex workflow run completed successfully
        status = result.get("status", "").upper()
        assert status == "COMPLETED", (
            f"Workflow run status was '{status}', expected 'COMPLETED'. "
            f"Full response: {result}"
        )

        # 3. Verify GitHub side-effect: the repo exists
        repo_data = gh_api("GET", f"/repos/{org}/{repo_name}")
        assert repo_data is not None, (
            f"Expected repo '{full_repo}' to exist after workflow run, but it was not found."
        )
        assert repo_data.get("name") == repo_name, (
            f"Expected repo name '{repo_name}', got '{repo_data.get('name')}'"
        )

        # 4. Set custom property for safety tracking
        gh_api("PATCH", f"/orgs/{org}/properties/values", input_data={
            "repository_names": [repo_name],
            "properties": [
                {"property_name": "cortex-cli-functional-test", "value": "true"}
            ],
        })
    finally:
        try:
            safe_delete_repo(full_repo)
        except RuntimeError:
            pass


@pytest.mark.functional
def test_gh_update_repository(gh_test_repo, gh_default_sha, import_functional_workflows):
    """Test the github.updateRepository workflow action block.

    Triggers a Cortex workflow that updates the test repository. Verifies
    the workflow run completes successfully.
    """
    # 1. Trigger the workflow to update the repository
    result = run_workflow(
        tag="func-test-gh-update-repository",
        initial_context={"repo": gh_test_repo},
    )

    # 2. Verify the Cortex workflow run completed successfully
    status = result.get("status", "").upper()
    assert status == "COMPLETED", (
        f"Workflow run status was '{status}', expected 'COMPLETED'. "
        f"Full response: {result}"
    )


@pytest.mark.functional
def test_gh_list_repositories(gh_test_repo, gh_default_sha, import_functional_workflows):
    """Test the github.listRepositories workflow action block.

    Triggers a Cortex workflow that lists repositories in the org, then
    verifies the list is non-empty via the gh API.
    """
    org = gh_test_repo.split("/")[0]

    # 1. Trigger the workflow to list repositories
    result = run_workflow(
        tag="func-test-gh-list-repositories",
        initial_context={"org": org},
    )

    # 2. Verify the Cortex workflow run completed successfully
    status = result.get("status", "").upper()
    assert status == "COMPLETED", (
        f"Workflow run status was '{status}', expected 'COMPLETED'. "
        f"Full response: {result}"
    )

    # 3. Verify GitHub side-effect: repos exist in the org
    repos = gh_api("GET", f"/orgs/{org}/repos")
    assert repos is not None and len(repos) > 0, (
        f"Expected to find repositories in org '{org}', but the list was empty."
    )
