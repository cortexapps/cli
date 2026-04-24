from playwright.sync_api import Page


def dismiss_admin_alert(page: Page):
    """Dismiss the 'Viewing tenant as admin' modal if it appears."""
    try:
        snooze = page.get_by_role("button", name="Snooze alert")
        snooze.wait_for(state="visible", timeout=3000)
        snooze.click()
    except Exception:
        pass
