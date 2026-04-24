import pytest
import re
from playwright.sync_api import Page, expect


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, playwright):
    return {"storage_state": "ui/state.json"}


def test_example(page: Page) -> None:
    page.goto("https://app.getcortexapp.com/admin/entities")
