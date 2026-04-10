import pytest
from tests.functional.gh_helpers import gh_api, run_workflow


@pytest.mark.functional
def test_gh_deployment_lifecycle(gh_test_repo, gh_default_sha, import_functional_workflows):
    """Test deployment lifecycle: create → get → list.

    Exercises github.createDeployment, github.getDeployment, and
    github.listDeployments workflow action blocks in a single flow.

    Note: GitHub deployments cannot be deleted via the API.
    """
    repo = gh_test_repo

    # 1. Create deployment via workflow
    result = run_workflow(
        tag="func-test-gh-create-deployment",
        initial_context={"repo": repo, "ref": "main"},
    )
    assert result.get("status", "").upper() == "COMPLETED", (
        f"createDeployment workflow failed: {result}"
    )

    # Verify: at least one deployment exists
    deployments = gh_api("GET", f"/repos/{repo}/deployments")
    assert deployments is not None and len(deployments) > 0, (
        f"Expected at least one deployment in {repo}, but the list was empty."
    )
    deployment_id = deployments[0]["id"]

    # 2. Get deployment via workflow
    result = run_workflow(
        tag="func-test-gh-get-deployment",
        initial_context={"repo": repo, "deployment-id": str(deployment_id)},
    )
    assert result.get("status", "").upper() == "COMPLETED", (
        f"getDeployment workflow failed: {result}"
    )

    # 3. List deployments via workflow
    result = run_workflow(
        tag="func-test-gh-list-deployments",
        initial_context={"repo": repo},
    )
    assert result.get("status", "").upper() == "COMPLETED", (
        f"listDeployments workflow failed: {result}"
    )
