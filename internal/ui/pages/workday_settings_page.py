import re

from playwright.sync_api import Page

from ui.pages.modals import dismiss_admin_alert

TIMEOUT = 15000


class WorkdaySettingsPage:
    """Cortex Workday integration settings page."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    def navigate(self):
        """Navigate to Integrations via sidebar, search for Workday."""
        self.page.goto(f"{self.base_url}/admin/home")
        dismiss_admin_alert(self.page)
        self.page.get_by_role("link", name="Integrations").click()
        self.page.wait_for_timeout(1000)
        self.page.get_by_role("textbox", name="Search integrations").fill("workday")
        self.page.wait_for_timeout(1000)

    def has_existing_configuration(self) -> bool:
        """Check if Workday is installed and configured (Settings link visible)."""
        try:
            settings_link = self.page.get_by_role("link", name="Settings")
            settings_link.wait_for(state="visible", timeout=3000)
            return True
        except Exception:
            return False

    def _go_to_settings(self):
        """Click the Settings link to enter the Workday config page."""
        self.page.get_by_role("link", name="Settings").click()
        self.page.wait_for_timeout(1000)

    def is_installed(self) -> bool:
        """Check if Workday integration is installed (not just configured)."""
        # If "Settings" is visible, it's installed and configured
        # If "Install" text is visible, it's not installed
        try:
            self.page.get_by_text("Install", exact=True).wait_for(state="visible", timeout=2000)
            return False
        except Exception:
            return True

    def install(self):
        """Install the Workday integration from the marketplace."""
        self.page.get_by_text("Install", exact=True).click()
        self.page.wait_for_timeout(2000)

    def delete_configuration(self):
        """Delete the existing Workday configuration. Stays on the settings page."""
        self._go_to_settings()
        self.page.get_by_role("button", name="Delete configuration").click()
        self.page.get_by_role("button", name="Delete").click()
        self.page.wait_for_timeout(2000)

    def configure(self, username: str, password: str, ownership_url: str):
        """Add a new Workday configuration with credentials and ownership report URL.

        Must already be on the Workday settings page (after install or delete).
        """
        self.page.locator("section").get_by_role("button", name="Add configuration").click()
        self.page.wait_for_timeout(1000)

        self.page.get_by_role("textbox", name="Username").fill(username)
        self.page.get_by_role("textbox", name="Password").fill(password)
        self.page.get_by_role("textbox", name="Ownership Report URL").fill(ownership_url)

        self.page.get_by_role("button", name="Save ⌘ ↩").click()
        self.page.wait_for_timeout(2000)

    def _select_dropdown_option(self, option_text: str):
        """Click the next available 'Select' dropdown and pick an option (first match)."""
        self.page.locator("div").filter(
            has_text=re.compile(r"^Select$")
        ).nth(1).click()
        self.page.get_by_text(option_text).first.click()

    def _select_dropdown_option_exact(self, option_text: str):
        """Click the next available 'Select' dropdown and pick an option by role (first match)."""
        self.page.locator("div").filter(
            has_text=re.compile(r"^Select$")
        ).nth(1).click()
        self.page.get_by_role("option", name=option_text, exact=True).first.click()

    def sync_teams(self):
        """Click 'Sync teams' to fetch available report fields."""
        self.page.get_by_role("button", name="Sync teams").click()
        self.page.wait_for_timeout(5000)

    def configure_employee_mappings(self):
        """Map employee fields: employeeId, email, firstName, lastName, employeeRole, managerEmail."""
        self._select_dropdown_option("employeeId")
        self._select_dropdown_option_exact("email")
        self._select_dropdown_option("firstName")
        self._select_dropdown_option("lastName")
        self._select_dropdown_option_exact("employeeRole")
        self._select_dropdown_option("managerEmail")
        self.page.get_by_role("button", name="Save").first.click()
        self.page.wait_for_timeout(1000)

    def configure_team_mappings(self):
        """Map team fields: teamDisplayId, teamDisplayName."""
        self._select_dropdown_option("teamDisplayId")
        self._select_dropdown_option("teamDisplayName")
        self.page.get_by_role("button", name="Save").nth(1).click()
        self.page.wait_for_timeout(1000)

    def configure_hierarchy_mappings(self):
        """Map hierarchy fields: employeeSupervisoryOrgId, teamSupervisoryOrgId."""
        self._select_dropdown_option("employeeSupervisoryOrgId")
        self._select_dropdown_option("teamSupervisoryOrgId")
        self.page.get_by_role("button", name="Save").nth(2).click()
        self.page.wait_for_timeout(1000)

    def configure_all_mappings(self):
        """Sync teams to fetch fields, then configure all three mapping sections."""
        self.sync_teams()
        self.configure_employee_mappings()
        self.configure_team_mappings()
        self.configure_hierarchy_mappings()

    def configure_fresh(self, username: str, password: str, ownership_url: str):
        """Delete existing config if present, install if needed, then configure.

        Handles three states:
        1. Configured: Settings → Delete → stays on page → Add configuration
        2. Installed but no config: Settings → already on settings page → Add configuration
        3. Not installed: Install → lands on settings page → Add configuration
        """
        if self.has_existing_configuration():
            # Installed and configured — delete first
            self.delete_configuration()
        elif self.is_installed():
            # Installed but no config — go to settings page
            self._go_to_settings()
        else:
            # Not installed — install first
            self.install()
        self.configure(username, password, ownership_url)
        self.configure_all_mappings()
