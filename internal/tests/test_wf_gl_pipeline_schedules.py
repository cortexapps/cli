import pytest
from tests.gl_helpers import gl_api, run_workflow, encode_project


@pytest.mark.functional
def test_gl_pipeline_schedule_lifecycle(gl_test_project, import_functional_workflows):
    """Test pipeline schedule lifecycle: create → get → list → update → delete.

    Exercises gitlab.createPipelineSchedule, gitlab.getPipelineSchedule,
    gitlab.listPipelineSchedules, gitlab.updatePipelineSchedule, and
    gitlab.deletePipelineSchedule workflow action blocks in a single flow.
    """
    project = gl_test_project
    encoded = encode_project(project)

    schedule_id = None
    try:
        # 1. Create pipeline schedule via workflow
        result = run_workflow(
            tag="func-test-gl-create-pipeline-schedule",
            initial_context={
                "project": project,
                "cron": "0 0 * * *",
                "pipeline-description": "cli-functional-test schedule",
                "ref": "main",
            },
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"createPipelineSchedule workflow failed: {result}"
        )

        # Find the created schedule
        schedules = gl_api("GET", f"projects/{encoded}/pipeline_schedules")
        matching = [s for s in schedules if "cli-functional-test" in s.get("description", "")]
        assert len(matching) > 0, (
            f"Expected pipeline schedule to exist after create."
        )
        schedule_id = matching[0]["id"]

        # 2. Get pipeline schedule via workflow
        result = run_workflow(
            tag="func-test-gl-get-pipeline-schedule",
            initial_context={
                "project": project,
                "pipeline-schedule-id": str(schedule_id),
            },
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"getPipelineSchedule workflow failed: {result}"
        )

        # 3. List pipeline schedules via workflow
        result = run_workflow(
            tag="func-test-gl-list-pipeline-schedules",
            initial_context={"project": project},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"listPipelineSchedules workflow failed: {result}"
        )

        # 4. Update pipeline schedule via workflow (changes cron to "0 1 * * *")
        result = run_workflow(
            tag="func-test-gl-update-pipeline-schedule",
            initial_context={
                "project": project,
                "pipeline-schedule-id": str(schedule_id),
            },
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"updatePipelineSchedule workflow failed: {result}"
        )

        # 5. Delete pipeline schedule via workflow
        result = run_workflow(
            tag="func-test-gl-delete-pipeline-schedule",
            initial_context={
                "project": project,
                "pipeline-schedule-id": str(schedule_id),
            },
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"deletePipelineSchedule workflow failed: {result}"
        )

        # Verify: schedule no longer exists
        try:
            gl_api("GET", f"projects/{encoded}/pipeline_schedules/{schedule_id}")
            assert False, (
                f"Expected pipeline schedule {schedule_id} to be deleted."
            )
        except RuntimeError:
            pass  # Expected: schedule is gone
    finally:
        if schedule_id is not None:
            try:
                gl_api("DELETE", f"projects/{encoded}/pipeline_schedules/{schedule_id}")
            except RuntimeError:
                pass
