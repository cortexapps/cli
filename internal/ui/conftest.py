import os
from pathlib import Path

import pytest
from playwright.sync_api import Playwright, Browser, BrowserContext, Page

from ui import config
from ui.pages.login_page import LoginPage
from ui.pages.google_auth_page import GoogleAuthPage
from ui.pages.modals import dismiss_admin_alert

_PW_DIR = Path(__file__).resolve().parent
STATE_FILE = str(_PW_DIR / "state.json")
VIDEO_DIR = str(_PW_DIR / "videos")


@pytest.fixture(scope="session")
def browser(playwright: Playwright):
    """Launch a headed Chromium browser."""
    browser = playwright.chromium.launch(
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--no-first-run",
        ],
    )
    yield browser
    browser.close()


def _create_context(browser: Browser, storage_state=None):
    """Create a browser context with WebAuthn disabled and optional saved state."""
    context = browser.new_context(
        record_video_dir=VIDEO_DIR,
        storage_state=storage_state,
    )
    # Disable WebAuthn/passkeys to prevent macOS native dialogs
    # that Playwright cannot interact with.
    context.add_init_script("""
        navigator.credentials.create = async () => { throw new Error('WebAuthn disabled'); };
        navigator.credentials.get = async () => { throw new Error('WebAuthn disabled'); };
    """)
    return context


def _do_full_login(browser: Browser) -> tuple[BrowserContext, Page]:
    """Perform full Google OAuth login and save session state."""
    context = _create_context(browser)
    page = context.new_page()

    login_page = LoginPage(page, config.BASE_URL, config.TENANT_CODE)
    login_page.navigate()
    login_page.click_sign_in_with_google()

    google_page = GoogleAuthPage(
        page,
        config.GOOGLE_EMAIL,
        config.GOOGLE_PASSWORD,
        config.GOOGLE_TOTP_URI,
    )
    google_page.complete_login()

    page.wait_for_url(f"{config.BASE_URL}/admin/**", timeout=30000)

    # Save session state for future runs
    context.storage_state(path=STATE_FILE)

    return context, page


def _try_cached_login(browser: Browser) -> tuple[BrowserContext, Page] | None:
    """Try to reuse saved session state. Returns None if expired."""
    if not os.path.exists(STATE_FILE):
        return None

    context = _create_context(browser, storage_state=STATE_FILE)
    page = context.new_page()
    page.goto(f"{config.BASE_URL}/admin/home")

    # Check if we land on the home page (session valid) or get redirected to login
    try:
        page.wait_for_url(f"{config.BASE_URL}/admin/**", timeout=10000)
        return context, page
    except Exception:
        # Session expired — clean up and return None
        context.close()
        os.remove(STATE_FILE)
        return None


@pytest.fixture(scope="session")
def authenticated_page(browser: Browser) -> Page:
    """Provide an authenticated Cortex page.

    Tries cached session state first. If expired or missing,
    performs full Google OAuth login and caches the new state.
    """
    # Try cached session first
    result = _try_cached_login(browser)
    if result:
        context, page = result
        dismiss_admin_alert(page)
        yield page
        context.close()
        return

    # Full login flow
    context, page = _do_full_login(browser)
    dismiss_admin_alert(page)
    yield page
    context.close()
