from pathlib import Path
import pytest
import re
from playwright.sync_api import Page, expect


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, playwright):
    return {"storage_state": str(Path(__file__).resolve().parent.parent / "state.json")}


def test_example(page: Page) -> None:
    page.goto("https://app.getcortexapp.com/admin/home")
    page.get_by_role("heading", name="Viewing tenant jeff-sandbox").click()
    page.get_by_role("button", name="Snooze alert").click()
    page.get_by_role("link", name="My entities").click()
    page.get_by_role("tab", name="Discovered entities").click()
