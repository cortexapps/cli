import base64

import pytest
from tests.gh_helpers import gh_api, run_workflow


@pytest.mark.functional
def test_gh_file_lifecycle(gh_test_repo, gh_default_sha, import_functional_workflows):
    """Test file lifecycle: create → get → find → delete.

    Exercises github.createOrUpdateFile, github.getFile, github.findFile,
    and github.deleteFile workflow action blocks in a single flow.
    """
    repo = gh_test_repo
    path = "cli-functional-test-file-lifecycle.txt"

    # Ensure the file does not exist before the test
    try:
        existing = gh_api("GET", f"/repos/{repo}/contents/{path}")
        if existing:
            gh_api("DELETE", f"/repos/{repo}/contents/{path}", input_data={
                "message": "cleanup before test",
                "sha": existing["sha"],
            })
    except RuntimeError:
        pass

    try:
        # 1. Create file via workflow
        result = run_workflow(
            tag="func-test-gh-create-or-update-file",
            initial_context={
                "repo": repo,
                "commit-message": "functional test",
                "content": base64.b64encode(b"test content").decode(),
                "path": path,
                "branch": "main",
            },
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"createOrUpdateFile workflow failed: {result}"
        )

        # Verify: file exists
        file_data = gh_api("GET", f"/repos/{repo}/contents/{path}")
        assert file_data is not None and file_data.get("path") == path, (
            f"Expected file '{path}' to exist after create, got: {file_data}"
        )

        # 2. Get file via workflow
        result = run_workflow(
            tag="func-test-gh-get-file",
            initial_context={"repo": repo, "path": path},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"getFile workflow failed: {result}"
        )

        # 3. Find file via workflow
        result = run_workflow(
            tag="func-test-gh-find-file",
            initial_context={"query": f"cli-functional-test-file-lifecycle repo:{repo}"},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"findFile workflow failed: {result}"
        )

        # 4. Delete file via workflow
        file_data = gh_api("GET", f"/repos/{repo}/contents/{path}")
        file_sha = file_data["sha"]

        result = run_workflow(
            tag="func-test-gh-delete-file",
            initial_context={
                "repo": repo,
                "path": path,
                "message": "delete test",
                "sha": file_sha,
            },
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"deleteFile workflow failed: {result}"
        )

        # Verify: file no longer exists
        try:
            gh_api("GET", f"/repos/{repo}/contents/{path}")
            assert False, (
                f"Expected file '{path}' to be deleted, but it still exists."
            )
        except RuntimeError:
            pass  # Expected: file is gone, GET returns 404
    finally:
        try:
            existing = gh_api("GET", f"/repos/{repo}/contents/{path}")
            if existing:
                gh_api("DELETE", f"/repos/{repo}/contents/{path}", input_data={
                    "message": "cleanup after test",
                    "sha": existing["sha"],
                })
        except RuntimeError:
            pass
