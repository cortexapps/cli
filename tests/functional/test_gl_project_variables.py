import pytest
from tests.functional.gl_helpers import gl_api, run_workflow, encode_project


@pytest.mark.functional
def test_gl_project_variable_lifecycle(gl_test_project, import_functional_workflows):
    """Test project variable lifecycle: create → get → list → update → delete.

    Exercises gitlab.createProjectVariable, gitlab.getProjectVariable,
    gitlab.listProjectVariables, gitlab.updateProjectVariable, and
    gitlab.deleteProjectVariable workflow action blocks in a single flow.
    """
    project = gl_test_project
    encoded = encode_project(project)
    var_key = "CLI_FUNCTIONAL_TEST_VAR"

    # Ensure the variable does not exist
    try:
        gl_api("DELETE", f"projects/{encoded}/variables/{var_key}")
    except RuntimeError:
        pass

    try:
        # 1. Create project variable via workflow
        result = run_workflow(
            tag="func-test-gl-create-project-variable",
            initial_context={
                "project": project,
                "key": var_key,
                "value": "initial-value",
            },
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"createProjectVariable workflow failed: {result}"
        )

        # Verify: variable exists
        var_data = gl_api("GET", f"projects/{encoded}/variables/{var_key}")
        assert var_data is not None and var_data.get("key") == var_key, (
            f"Expected variable '{var_key}' to exist after create."
        )

        # 2. Get project variable via workflow
        result = run_workflow(
            tag="func-test-gl-get-project-variable",
            initial_context={"project": project, "key": var_key},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"getProjectVariable workflow failed: {result}"
        )

        # 3. List project variables via workflow
        result = run_workflow(
            tag="func-test-gl-list-project-variables",
            initial_context={"project": project},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"listProjectVariables workflow failed: {result}"
        )

        # 4. Update project variable via workflow
        result = run_workflow(
            tag="func-test-gl-update-project-variable",
            initial_context={
                "project": project,
                "key": var_key,
                "value": "updated-value",
            },
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"updateProjectVariable workflow failed: {result}"
        )

        # Verify: value updated
        var_data = gl_api("GET", f"projects/{encoded}/variables/{var_key}")
        assert var_data.get("value") == "updated-value", (
            f"Expected value 'updated-value', got: '{var_data.get('value')}'"
        )

        # 5. Delete project variable via workflow
        result = run_workflow(
            tag="func-test-gl-delete-project-variable",
            initial_context={"project": project, "key": var_key},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"deleteProjectVariable workflow failed: {result}"
        )

        # Verify: variable no longer exists
        try:
            gl_api("GET", f"projects/{encoded}/variables/{var_key}")
            assert False, (
                f"Expected variable '{var_key}' to be deleted."
            )
        except RuntimeError:
            pass  # Expected: variable is gone
    finally:
        try:
            gl_api("DELETE", f"projects/{encoded}/variables/{var_key}")
        except RuntimeError:
            pass
