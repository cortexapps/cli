import base64
import time

import pytest
from tests.functional.gh_helpers import gh_api, run_workflow


@pytest.mark.functional
def test_gh_branch_lifecycle(gh_test_repo, gh_default_sha, import_functional_workflows):
    """Test branch lifecycle: create → get → rename → delete.

    Exercises github.createBranch, github.getBranch, github.renameBranch,
    and github.deleteBranch workflow action blocks in a single flow.
    """
    branch_name = "cli-functional-test-branch-lifecycle"
    renamed_branch = "cli-functional-test-branch-lifecycle-renamed"

    # Ensure neither branch exists before the test
    for name in (branch_name, renamed_branch):
        try:
            gh_api("DELETE", f"/repos/{gh_test_repo}/git/refs/heads/{name}")
        except RuntimeError:
            pass

    try:
        # 1. Create branch via workflow
        result = run_workflow(
            tag="func-test-gh-create-branch",
            initial_context={"repo": gh_test_repo, "new-branch": branch_name, "sha": gh_default_sha},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"createBranch workflow failed: {result}"
        )

        # Verify: branch exists
        branches = gh_api("GET", f"/repos/{gh_test_repo}/branches")
        branch_names = [b["name"] for b in branches]
        assert branch_name in branch_names, (
            f"Expected branch '{branch_name}' to exist, got: {branch_names}"
        )

        # 2. Get branch via workflow
        result = run_workflow(
            tag="func-test-gh-get-branch",
            initial_context={"repo": gh_test_repo, "branch": branch_name},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"getBranch workflow failed: {result}"
        )

        # 3. Rename branch via workflow
        result = run_workflow(
            tag="func-test-gh-rename-branch",
            initial_context={
                "repo": gh_test_repo,
                "current-branch": branch_name,
                "new-branch": renamed_branch,
            },
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"renameBranch workflow failed: {result}"
        )

        # Verify: old name gone, new name exists (poll for async rename)
        for _ in range(10):
            branches = gh_api("GET", f"/repos/{gh_test_repo}/branches")
            branch_names = [b["name"] for b in branches]
            if branch_name not in branch_names and renamed_branch in branch_names:
                break
            time.sleep(1)
        assert branch_name not in branch_names, (
            f"Expected old branch '{branch_name}' to be gone, got: {branch_names}"
        )
        assert renamed_branch in branch_names, (
            f"Expected renamed branch '{renamed_branch}' to exist, got: {branch_names}"
        )

        # 4. Delete the renamed branch via workflow
        result = run_workflow(
            tag="func-test-gh-delete-branch",
            initial_context={"repo": gh_test_repo, "branch": renamed_branch},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"deleteBranch workflow failed: {result}"
        )

        # Verify: branch no longer exists
        branches = gh_api("GET", f"/repos/{gh_test_repo}/branches")
        branch_names = [b["name"] for b in branches]
        assert renamed_branch not in branch_names, (
            f"Expected branch '{renamed_branch}' to be deleted, got: {branch_names}"
        )
    finally:
        for name in (branch_name, renamed_branch):
            try:
                gh_api("DELETE", f"/repos/{gh_test_repo}/git/refs/heads/{name}")
            except RuntimeError:
                pass


@pytest.mark.functional
def test_gh_merge_branch(gh_test_repo, gh_default_sha, import_functional_workflows):
    """Test the github.mergeBranch workflow action block.

    Creates a branch with a file commit, then triggers a Cortex workflow that
    merges it into main. Verifies the merge commit exists on main.
    """
    branch_name = "cli-functional-test-merge-branch"
    file_path = "cli-functional-test-merge-file.txt"

    try:
        gh_api("DELETE", f"/repos/{gh_test_repo}/git/refs/heads/{branch_name}")
    except RuntimeError:
        pass

    gh_api("POST", f"/repos/{gh_test_repo}/git/refs", input_data={
        "ref": f"refs/heads/{branch_name}",
        "sha": gh_default_sha,
    })

    try:
        gh_api("PUT", f"/repos/{gh_test_repo}/contents/{file_path}", input_data={
            "message": "test commit for merge functional test",
            "content": base64.b64encode(b"cli functional test content").decode(),
            "branch": branch_name,
        })

        result = run_workflow(
            tag="func-test-gh-merge-branch",
            initial_context={
                "repo": gh_test_repo,
                "base-branch": "main",
                "head-branch": branch_name,
            },
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"mergeBranch workflow failed: {result}"
        )

        commits = gh_api("GET", f"/repos/{gh_test_repo}/commits?path={file_path}&sha=main")
        assert len(commits) > 0, (
            f"Expected merge commit for '{file_path}' on main, but found none."
        )
    finally:
        try:
            gh_api("DELETE", f"/repos/{gh_test_repo}/git/refs/heads/{branch_name}")
        except RuntimeError:
            pass


@pytest.mark.functional
def test_gh_list_branches(gh_test_repo, gh_default_sha, import_functional_workflows):
    """Test the github.listBranches workflow action block."""
    result = run_workflow(
        tag="func-test-gh-list-branches",
        initial_context={"repo": gh_test_repo},
    )
    assert result.get("status", "").upper() == "COMPLETED", (
        f"listBranches workflow failed: {result}"
    )

    branches = gh_api("GET", f"/repos/{gh_test_repo}/branches")
    branch_names = [b["name"] for b in branches]
    assert "main" in branch_names, (
        f"Expected 'main' branch in repo {gh_test_repo}, got: {branch_names}"
    )


@pytest.mark.functional
def test_gh_create_reference(gh_test_repo, gh_default_sha, import_functional_workflows):
    """Test the github.createReference workflow action block."""
    ref_name = "cli-functional-test-create-ref"
    full_ref = f"refs/heads/{ref_name}"

    try:
        gh_api("DELETE", f"/repos/{gh_test_repo}/git/refs/heads/{ref_name}")
    except RuntimeError:
        pass

    try:
        result = run_workflow(
            tag="func-test-gh-create-reference",
            initial_context={"repo": gh_test_repo, "ref": full_ref, "sha": gh_default_sha},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"createReference workflow failed: {result}"
        )

        branches = gh_api("GET", f"/repos/{gh_test_repo}/branches")
        branch_names = [b["name"] for b in branches]
        assert ref_name in branch_names, (
            f"Expected ref '{ref_name}' to exist as a branch, got: {branch_names}"
        )
    finally:
        try:
            gh_api("DELETE", f"/repos/{gh_test_repo}/git/refs/heads/{ref_name}")
        except RuntimeError:
            pass
