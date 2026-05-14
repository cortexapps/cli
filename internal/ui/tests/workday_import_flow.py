import pytest
import re
from playwright.sync_api import Page, expect


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, playwright):
    return {"storage_state": "ui/state.json"}


def test_example(page: Page) -> None:
    page.goto("https://app.getcortexapp.com/admin/entities")
    page.locator(".fixed.inset-0").first.click()
    page.get_by_role("tabpanel", name="Entities").click()
    page.get_by_role("link", name="All entities").click()
    page.get_by_role("link", name="Import entities").click()
    page.locator(".shadow-xs").first.click()
    page.get_by_role("button", name="Workday logo image Workday").click()
    page.get_by_text("Entity").click()
    page.get_by_role("row", name="Entity").get_by_role("checkbox").click()
    page.get_by_role("button", name="Next step ⌘ ↩").click()
    page.get_by_role("button", name="Confirm import ⌘ ↩").click()
    page.get_by_role("link", name="Continue to all entities ⌘ ↩").click()
