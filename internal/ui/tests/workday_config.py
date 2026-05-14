"""Workday integration config — works whether or not a config already exists.

This is a codegen-style recording, not a proper test. Use test_workday.py for
the real test suite. This file is useful for quick manual runs and as a
selector reference.
"""

import os

import pytest
from playwright.sync_api import Page

from ui.api.cortex_api import CortexAPI

ENTITY_PREFIX = "pw-"


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, playwright):
    return {"storage_state": "ui/state.json"}


def test_configure_workday(page: Page) -> None:
    username = os.environ.get("WORKDAY_USERNAME", "myTestUser")
    password = os.environ.get("WORKDAY_PASSWORD", "myTestPassword")
    ownership_url = os.environ.get(
        "WORKDAY_OWNERSHIP_REPORT_URL",
        "https://mp15fcb2b4f645b182f1.free.beeceptor.com/data",
    )

    # --- Cleanup: delete any previously imported entities ---
    api = CortexAPI()
    deleted = api.delete_entities_by_prefix(ENTITY_PREFIX)
    if deleted:
        print(f"Cleaned up {len(deleted)} entities: {deleted}")

    # --- Navigate to Integrations via sidebar ---
    page.goto("https://app.getcortexapp.com/admin/home")

    # Dismiss admin alert if present
    try:
        snooze = page.get_by_role("button", name="Snooze alert")
        snooze.wait_for(state="visible", timeout=3000)
        snooze.click()
    except Exception:
        pass

    page.get_by_role("link", name="Integrations").click()
    page.wait_for_timeout(1000)

    # Search for Workday
    page.get_by_role("textbox", name="Search integrations").fill("workday")
    page.wait_for_timeout(1000)

    # Delete existing configuration if present
    try:
        settings_link = page.get_by_role("link", name="Settings")
        settings_link.wait_for(state="visible", timeout=3000)
        settings_link.click()
        page.get_by_role("button", name="Delete configuration").click()
        page.get_by_role("button", name="Delete").click()
        page.wait_for_timeout(2000)

        # Re-navigate after deletion
        page.get_by_role("link", name="Integrations").click()
        page.wait_for_timeout(1000)
        page.get_by_role("textbox", name="Search integrations").fill("workday")
        page.wait_for_timeout(1000)
    except Exception:
        pass  # No existing configuration — proceed to create

    # Add new configuration
    page.locator("section").get_by_role("button", name="Add configuration").click()
    page.wait_for_timeout(1000)

    # Fill credentials
    page.get_by_role("textbox", name="Username").fill(username)
    page.get_by_role("textbox", name="Password").fill(password)

    # Fill ownership report URL
    page.get_by_role("textbox", name="Ownership Report URL").fill(ownership_url)

    # Save configuration
    page.get_by_role("button", name="Save ⌘ ↩").click()
    page.wait_for_timeout(2000)

    # DEBUG: pause here to inspect the page and figure out the import flow
    page.pause()
