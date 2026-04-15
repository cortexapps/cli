import base64

import pytest
from tests.functional.gl_helpers import gl_api, run_workflow, encode_project


@pytest.mark.functional
def test_gl_file_lifecycle(gl_test_project, import_functional_workflows):
    """Test file lifecycle: create → get → update → delete.

    Exercises gitlab.createFile, gitlab.getFile, gitlab.updateFile,
    and gitlab.deleteFile workflow action blocks in a single flow.
    """
    project = gl_test_project
    encoded = encode_project(project)
    path = "cli-functional-test-file.txt"

    # Ensure the file does not exist
    try:
        gl_api("DELETE", f"projects/{encoded}/repository/files/{path}", input_data={
            "branch": "main",
            "commit_message": "cleanup before test",
        })
    except RuntimeError:
        pass

    try:
        # 1. Create file via workflow
        content = base64.b64encode(b"test content").decode()
        result = run_workflow(
            tag="func-test-gl-create-file",
            initial_context={
                "project": project,
                "path": path,
                "branch": "main",
                "message": "create test file",
                "content": content,
            },
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"createFile workflow failed: {result}"
        )

        # Verify: file exists
        file_data = gl_api("GET", f"projects/{encoded}/repository/files/{path}?ref=main")
        assert file_data is not None, (
            f"Expected file '{path}' to exist after create."
        )

        # 2. Get file via workflow
        result = run_workflow(
            tag="func-test-gl-get-file",
            initial_context={"project": project, "path": path, "ref": "main"},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"getFile workflow failed: {result}"
        )

        # 3. Update file via workflow
        updated_content = base64.b64encode(b"updated content").decode()
        result = run_workflow(
            tag="func-test-gl-update-file",
            initial_context={
                "project": project,
                "path": path,
                "branch": "main",
                "message": "update test file",
                "content": updated_content,
            },
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"updateFile workflow failed: {result}"
        )

        # 4. Delete file via workflow
        result = run_workflow(
            tag="func-test-gl-delete-file",
            initial_context={
                "project": project,
                "path": path,
                "branch": "main",
                "message": "delete test file",
            },
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"deleteFile workflow failed: {result}"
        )

        # Verify: file no longer exists
        try:
            gl_api("GET", f"projects/{encoded}/repository/files/{path}?ref=main")
            assert False, (
                f"Expected file '{path}' to be deleted, but it still exists."
            )
        except RuntimeError:
            pass  # Expected: file is gone
    finally:
        try:
            gl_api("DELETE", f"projects/{encoded}/repository/files/{path}", input_data={
                "branch": "main",
                "commit_message": "cleanup after test",
            })
        except RuntimeError:
            pass
