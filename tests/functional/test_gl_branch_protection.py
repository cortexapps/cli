import pytest
from tests.functional.gl_helpers import gl_api, run_workflow, encode_project


@pytest.mark.functional
def test_gl_branch_protection_lifecycle(gl_test_project, import_functional_workflows):
    """Test branch protection lifecycle: create → get → list → update → delete.

    Exercises gitlab.createBranchProtection, gitlab.getProtectedBranch,
    gitlab.listProtectedBranches, gitlab.updateBranchProtection, and
    gitlab.deleteBranchProtection workflow action blocks in a single flow.
    """
    project = gl_test_project
    encoded = encode_project(project)
    branch_name = "main"

    # Ensure no existing protection on main (GitLab auto-protects main)
    try:
        gl_api("DELETE", f"projects/{encoded}/protected_branches/{branch_name}")
    except RuntimeError:
        pass

    try:
        # 1. Create branch protection via workflow
        result = run_workflow(
            tag="func-test-gl-create-branch-protection",
            initial_context={"project": project, "branch-name": branch_name},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"createBranchProtection workflow failed: {result}"
        )

        # Verify: branch is protected
        protection = gl_api("GET", f"projects/{encoded}/protected_branches/{branch_name}")
        assert protection is not None, (
            f"Expected branch '{branch_name}' to be protected."
        )

        # 2. Get protected branch via workflow
        result = run_workflow(
            tag="func-test-gl-get-protected-branch",
            initial_context={"project": project, "branch-name": branch_name},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"getProtectedBranch workflow failed: {result}"
        )

        # 3. List protected branches via workflow
        result = run_workflow(
            tag="func-test-gl-list-protected-branches",
            initial_context={"project": project},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"listProtectedBranches workflow failed: {result}"
        )

        # 4. Update branch protection via workflow (sets allow_force_push=true)
        result = run_workflow(
            tag="func-test-gl-update-branch-protection",
            initial_context={"project": project, "branch-name": branch_name},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"updateBranchProtection workflow failed: {result}"
        )

        # 5. Delete branch protection via workflow
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
    finally:
        try:
            gl_api("DELETE", f"projects/{encoded}/protected_branches/{branch_name}")
        except RuntimeError:
            pass
