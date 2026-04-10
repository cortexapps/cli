import pytest
from tests.functional.gl_helpers import gl_api, run_workflow, encode_project


@pytest.mark.functional
def test_gl_push_rule_lifecycle(gl_test_project, import_functional_workflows):
    """Test push rule lifecycle: create → get → delete.

    Exercises gitlab.createPushRule, gitlab.getPushRule, and
    gitlab.deletePushRule workflow action blocks in a single flow.

    Note: gitlab.updatePushRule is not yet published and is skipped.
    Push rules may require GitLab Premium. This test will fail with
    a clear error if the feature is not available.
    """
    project = gl_test_project
    encoded = encode_project(project)

    # Ensure no existing push rule
    try:
        gl_api("DELETE", f"projects/{encoded}/push_rule")
    except RuntimeError:
        pass

    try:
        # 1. Create push rule via workflow (sets prevent_secrets=true)
        result = run_workflow(
            tag="func-test-gl-create-push-rule",
            initial_context={"project": project},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"createPushRule workflow failed: {result}"
        )

        # Verify: push rule exists
        rule = gl_api("GET", f"projects/{encoded}/push_rule")
        assert rule is not None, (
            f"Expected push rule to exist after create."
        )

        # 2. Get push rule via workflow
        result = run_workflow(
            tag="func-test-gl-get-push-rule",
            initial_context={"project": project},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"getPushRule workflow failed: {result}"
        )

        # 3. Delete push rule via workflow
        result = run_workflow(
            tag="func-test-gl-delete-push-rule",
            initial_context={"project": project},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"deletePushRule workflow failed: {result}"
        )

        # Verify: push rule no longer exists
        try:
            gl_api("GET", f"projects/{encoded}/push_rule")
            assert False, (
                f"Expected push rule to be deleted."
            )
        except RuntimeError:
            pass  # Expected: push rule is gone
    finally:
        try:
            gl_api("DELETE", f"projects/{encoded}/push_rule")
        except RuntimeError:
            pass
