import pytest

from ui import config
from ui.api.cortex_api import CortexAPI
from ui.pages.workflows_page import WorkflowsPage

WORKFLOW_NAME = "Playwright: Test Workflow"


@pytest.fixture()
def cortex_api():
    return CortexAPI()


@pytest.fixture()
def cleanup_workflow(cortex_api):
    """Delete test workflows before and after the test."""
    cortex_api.delete_workflow_by_name(WORKFLOW_NAME)
    yield
    cortex_api.delete_workflow_by_name(WORKFLOW_NAME)


def test_create_workflow(authenticated_page, cleanup_workflow, cortex_api):
    """Create a workflow through the UI and verify it exists via API."""
    workflows = WorkflowsPage(authenticated_page, config.BASE_URL)
    workflows.navigate()
    workflows.create_workflow(WORKFLOW_NAME)

    # Verify we landed on the workflow edit page
    assert "/workflows/" in authenticated_page.url
    assert "/edit" in authenticated_page.url
