import os
import time

import pytest

from ui import config
from ui.api.cortex_api import CortexAPI
from ui.pages.workday_settings_page import WorkdaySettingsPage

# Skip entire module if Workday credentials are not configured
pytestmark = pytest.mark.skipif(
    not os.getenv("WORKDAY_USERNAME"),
    reason="WORKDAY_USERNAME not set — skipping Workday tests",
)

ENTITY_PREFIX = "pw-"
POLL_INTERVAL = 15  # seconds
POLL_TIMEOUT = 120  # 2 minutes


@pytest.fixture(scope="module")
def cortex_api():
    return CortexAPI()


@pytest.fixture(scope="module")
def workday_page(authenticated_page):
    return WorkdaySettingsPage(authenticated_page, config.BASE_URL)


@pytest.fixture(scope="module")
def workday_creds():
    return {
        "username": os.environ["WORKDAY_USERNAME"],
        "password": os.environ["WORKDAY_PASSWORD"],
        "ownership_url": os.environ["WORKDAY_OWNERSHIP_REPORT_URL"],
    }


class TestWorkdayIntegration:
    """Sequential tests for Workday integration: cleanup → configure → import → verify."""

    def test_cleanup_previous_entities(self, cortex_api):
        """Delete any entities from a previous Workday test run."""
        deleted = cortex_api.delete_entities_by_prefix(ENTITY_PREFIX)
        if deleted:
            print(f"Cleaned up {len(deleted)} entities: {deleted}")

    def test_configure_workday(self, workday_page, workday_creds):
        """Configure Workday integration with credentials, URL, and field mappings."""
        workday_page.navigate()
        workday_page.configure_fresh(**workday_creds)

    def test_import_discovered_entities(self, authenticated_page):
        """Navigate to entity import, sync Workday, select all, and import."""
        page = authenticated_page

        # Navigate to All entities page, then Import entities
        page.goto(f"{config.BASE_URL}/admin/entities")
        page.wait_for_timeout(1000)
        page.get_by_role("link", name="Import entities").click()
        page.wait_for_timeout(1000)

        # Select "Import discovered entities"
        page.locator(".shadow-xs").first.click()
        page.wait_for_timeout(1000)

        # Select Workday as the import source
        page.get_by_role("button", name="Workday logo image Workday").click()
        page.wait_for_timeout(1000)

        # Sync entities to discover Workday teams
        page.get_by_role("button", name="Sync entities").click()
        page.wait_for_timeout(10000)

        # Select all discovered entities via header checkbox
        page.get_by_role("row", name="Entity").get_by_role("checkbox").click()
        page.wait_for_timeout(500)

        # Next step → Confirm import → Continue
        page.get_by_role("button", name="Next step").click()
        page.wait_for_timeout(1000)
        page.get_by_role("button", name="Confirm import").click()
        page.wait_for_timeout(3000)
        page.get_by_role("link", name="Continue to all entities").click()
        page.wait_for_timeout(1000)

    def test_verify_imported_entities(self, cortex_api):
        """Verify entities with pw- prefix were imported."""
        deadline = time.time() + POLL_TIMEOUT
        workday_entities = []

        while time.time() < deadline:
            entities = cortex_api.list_catalog()
            workday_entities = [
                e for e in entities if e.get("tag", "").startswith(ENTITY_PREFIX)
            ]
            if workday_entities:
                break
            time.sleep(POLL_INTERVAL)

        assert workday_entities, (
            f"No entities with prefix '{ENTITY_PREFIX}' found after import. "
            f"Total entities: {len(entities)}"
        )
        print(f"Found {len(workday_entities)} Workday entities:")
        for entity in workday_entities:
            print(f"  {entity['tag']}")
