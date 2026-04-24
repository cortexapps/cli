import pytest
from tests.gl_helpers import gl_api, run_workflow, encode_project


@pytest.mark.functional
def test_gl_branch_protection_lifecycle(gl_test_project, import_functional_workflows):
    """Test branch protection lifecycle: get → list → update → delete → create.

    GitLab auto-protects 'main' on new projects, so we start with the
    existing protection and end by re-creating it after delete.

    Exercises gitlab.getProtectedBranch, gitlab.listProtectedBranches,
    gitlab.updateBranchProtection, gitlab.deleteBranchProtection, and
    gitlab.createBranchProtection workflow action blocks in a single flow.
    """
    project = gl_test_project
    encoded = encode_project(project)
    branch_name = "main"

    try:
        # 1. Get protected branch via workflow (main is auto-protected)
        result = run_workflow(
            tag="func-test-gl-get-protected-branch",
            initial_context={"project": project, "branch-name": branch_name},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"getProtectedBranch workflow failed: {result}"
        )

        # 2. List protected branches via workflow
        result = run_workflow(
            tag="func-test-gl-list-protected-branches",
            initial_context={"project": project},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"listProtectedBranches workflow failed: {result}"
        )

        # 3. Update branch protection via workflow (sets allow_force_push=true)
        result = run_workflow(
            tag="func-test-gl-update-branch-protection",
            initial_context={"project": project, "branch-name": branch_name},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"updateBranchProtection workflow failed: {result}"
        )

        # 4. Delete branch protection via workflow
        result = run_workflow(
            tag="func-test-gl-delete-branch-protection",
            initial_context={"project": project, "branch-name": branch_name},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"deleteBranchProtection workflow failed: {result}"
        )

        # Verify: branch is no longer protected
        try:
            gl_api("GET", f"projects/{encoded}/protected_branches/{branch_name}")
            assert False, (
                f"Expected branch '{branch_name}' protection to be deleted."
            )
        except RuntimeError:
            pass  # Expected: protection is gone

        # 5. Create branch protection via workflow (re-protect main)
        result = run_workflow(
            tag="func-test-gl-create-branch-protection",
            initial_context={"project": project, "branch-name": branch_name},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"createBranchProtection workflow failed: {result}"
        )

        # Verify: branch is protected again
        protection = gl_api("GET", f"projects/{encoded}/protected_branches/{branch_name}")
        assert protection is not None, (
            f"Expected branch '{branch_name}' to be protected."
        )
    finally:
        # Ensure main is re-protected for other tests
        try:
            gl_api("POST", f"projects/{encoded}/protected_branches",
                   input_data={"name": branch_name})
        except RuntimeError:
            pass
