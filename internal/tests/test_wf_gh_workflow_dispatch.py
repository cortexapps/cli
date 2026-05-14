import base64
import time

import pytest
from tests.gh_helpers import gh_api, run_workflow


@pytest.mark.functional
def test_gh_create_workflow_dispatch_event(gh_test_repo, gh_default_sha, import_functional_workflows):
    """Test the github.createWorkflowDispatchEvent action block."""
    # Create a minimal GitHub Actions workflow file in the repo
    workflow_content = """name: test-dispatch
on:
  workflow_dispatch:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "dispatched"
"""
    workflow_path = ".github/workflows/cli-functional-test-dispatch.yml"
    encoded = base64.b64encode(workflow_content.encode()).decode()

    try:
        # Create the workflow file
        gh_api("PUT", f"/repos/{gh_test_repo}/contents/{workflow_path}", input_data={
            "message": "add test dispatch workflow",
            "content": encoded,
        })

        # Give GitHub a moment to register the workflow
        time.sleep(3)

        # Trigger the dispatch via Cortex workflow
        result = run_workflow(
            tag="func-test-gh-create-workflow-dispatch-event",
            initial_context={
                "repo": gh_test_repo,
                "ref": "main",
                "workflow-id": "cli-functional-test-dispatch.yml",
            },
        )

        status = result.get("status", "").upper()
        assert status == "COMPLETED", (
            f"Workflow run status was '{status}', expected 'COMPLETED'. "
            f"Full response: {result}"
        )
    finally:
        # Clean up: delete the workflow file
        try:
            file_info = gh_api("GET", f"/repos/{gh_test_repo}/contents/{workflow_path}")
            gh_api("DELETE", f"/repos/{gh_test_repo}/contents/{workflow_path}", input_data={
                "message": "cleanup test dispatch workflow",
                "sha": file_info["sha"],
            })
        except RuntimeError:
            pass
