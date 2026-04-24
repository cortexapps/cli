from ui import config


def test_google_login_reaches_home(authenticated_page):
    """Verify that Google OAuth login lands on the Cortex admin home page."""
    authenticated_page.goto(f"{config.BASE_URL}/admin/home")
    assert "/admin/home" in authenticated_page.url


def test_google_login_page_title(authenticated_page):
    """Verify the page title after login."""
    authenticated_page.goto(f"{config.BASE_URL}/admin/home")
    assert "Cortex" in authenticated_page.title()
