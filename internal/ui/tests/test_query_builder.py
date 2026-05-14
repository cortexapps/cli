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
    page.get_by_role("button", name="Tools").click()
    page.get_by_role("link", name="Query builder").click()
    page.locator(".ace_content").click()
    page.get_by_role("textbox", name="CQL query").fill("entity.tag() == \"california\"\n\n")
    page.locator("div").filter(has_text=re.compile(r"^Select entities$")).nth(1).click()
    page.get_by_role("combobox", name="Search").fill("california")
    page.get_by_text("California (california)").click()
    page.get_by_role("button", name="Test ⌘ ↩").click()
    page.get_by_role("cell", name="True").click()
