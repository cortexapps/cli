from pathlib import Path
import pytest
import re
from playwright.sync_api import Page, expect


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, playwright):
    return {"storage_state": str(Path(__file__).resolve().parent.parent / "state.json")}


def test_example(page: Page) -> None:
    page.goto("https://app.getcortexapp.com/admin/home")
    page.get_by_role("tab", name="hours").click()
    page.get_by_role("button", name="Snooze alert").click()
    page.get_by_role("button", name="Search (Command/Control + K)").click()
    page.get_by_role("textbox", name="Search in Cortex").fill("cli-test")
    page.get_by_role("textbox", name="Search in Cortex").press("Enter")
    page.get_by_role("link", name="Service CLI Test Create").click()
    page.get_by_role("button", name="Owners").click()
