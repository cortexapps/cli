import pytest
from tests.gl_helpers import (
    gl_api, run_workflow, encode_project, safe_delete_project,
    get_authenticated_user, RESOURCE_PREFIX,
)


@pytest.mark.functional
def test_gl_project_lifecycle(gl_test_namespace, import_functional_workflows):
    """Test project lifecycle: create → get → update → archive → unarchive → delete.

    Exercises gitlab.createProject, gitlab.getProject, gitlab.updateProject,
    gitlab.archiveProject, gitlab.unarchiveProject, and gitlab.deleteProject
    workflow action blocks in a single flow.
    """
    project_name = "cli-functional-test-project-lifecycle"
    project_path = f"{gl_test_namespace}/{project_name}"
    encoded = encode_project(project_path)

    # Ensure the project does not exist before the test
    safe_delete_project(project_path)

    try:
        # 1. Create project via workflow
        result = run_workflow(
            tag="func-test-gl-create-project",
            initial_context={"project-name": project_name},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"createProject workflow failed: {result}"
        )

        # Verify: project exists
        project = gl_api("GET", f"projects/{encoded}")
        assert project is not None, (
            f"Expected project '{project_path}' to exist after create."
        )

        # 2. Get project via workflow
        result = run_workflow(
            tag="func-test-gl-get-project",
            initial_context={"project": project_path},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"getProject workflow failed: {result}"
        )

        # 3. Update project via workflow
        result = run_workflow(
            tag="func-test-gl-update-project",
            initial_context={
                "project": project_path,
                "project-description": "Updated by functional test",
            },
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"updateProject workflow failed: {result}"
        )

        # Verify: description updated
        project = gl_api("GET", f"projects/{encoded}")
        assert project.get("description") == "Updated by functional test", (
            f"Expected description 'Updated by functional test', "
            f"got: '{project.get('description')}'"
        )

        # 4. Archive project via workflow
        result = run_workflow(
            tag="func-test-gl-archive-project",
            initial_context={"project": project_path},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"archiveProject workflow failed: {result}"
        )

        # Verify: project is archived
        project = gl_api("GET", f"projects/{encoded}")
        assert project.get("archived") is True, (
            f"Expected project to be archived, got: {project.get('archived')}"
        )

        # 5. Unarchive project via workflow
        result = run_workflow(
            tag="func-test-gl-unarchive-project",
            initial_context={"project": project_path},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"unarchiveProject workflow failed: {result}"
        )

        # Verify: project is no longer archived
        project = gl_api("GET", f"projects/{encoded}")
        assert project.get("archived") is False, (
            f"Expected project to be unarchived, got: {project.get('archived')}"
        )

        # 6. Delete project via workflow
        result = run_workflow(
            tag="func-test-gl-delete-project",
            initial_context={"project": project_path},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"deleteProject workflow failed: {result}"
        )

        # Verify: project no longer exists
        try:
            gl_api("GET", f"projects/{encoded}")
            assert False, (
                f"Expected project '{project_path}' to be deleted, but it still exists."
            )
        except RuntimeError:
            pass  # Expected: project is gone
    finally:
        safe_delete_project(project_path)
