import re

from playwright.sync_api import Page

from ui.pages.modals import dismiss_admin_alert

TIMEOUT = 15000


class WorkflowsPage:
    """Cortex Workflows page — list, create, and configure workflows."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    def navigate(self):
        self.page.goto(f"{self.base_url}/admin/workflows")
        dismiss_admin_alert(self.page)

    def click_create_workflow(self):
        self.page.get_by_role("link", name="Create workflow").click()

    def click_start_from_scratch(self):
        self.page.get_by_role("button", name="Start from scratch").click()

    def fill_name(self, name: str):
        self.page.get_by_role("textbox", name="Workflow name").click()
        self.page.get_by_role("textbox", name="Workflow name").fill(name)

    def click_create(self):
        self.page.get_by_role("button", name="Create").click()
        self.page.wait_for_url("**/workflows/*/edit", timeout=TIMEOUT)

    def set_scope_to_service(self):
        """Select Entity scope, then pick Service."""
        self.page.get_by_role("combobox", name="Scope").click()
        self.page.get_by_role("option", name="Entity").click()
        self.page.locator("div").filter(has_text=re.compile(r"^Select$")).nth(1).click()
        self.page.get_by_role("combobox", name="Search").fill("service")
        self.page.get_by_role("combobox", name="Search").press("Enter")

    def click_save(self):
        self.page.get_by_role("button", name="Save ⌘ ↩").click()

    def create_workflow(self, name: str):
        """Full workflow creation: create → name → create → scope to service → save."""
        self.click_create_workflow()
        self.click_start_from_scratch()
        self.fill_name(name)
        self.click_create()
        self.set_scope_to_service()
        self.click_save()
