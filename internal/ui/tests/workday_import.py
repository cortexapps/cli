import pytest
import re
from playwright.sync_api import Page, expect


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, playwright):
    return {"storage_state": "ui/state.json"}


def test_example(page: Page) -> None:
    page.goto("https://app.getcortexapp.com/admin/entities")
    page.get_by_text("Please be cautious with actions in this environment.5 minutes30 minutes24 hours").click()
    page.get_by_role("button", name="Snooze alert").click()
    page.get_by_role("link", name="Import entities").click()
    page.locator(".shadow-xs").first.click()
    page.get_by_role("button", name="Workday logo image Workday").click()
    page.get_by_role("button", name="Sync entities").click()
    page.get_by_role("button", name="Next step ⌘ ↩").click()
