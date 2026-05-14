from playwright.sync_api import Page


class LoginPage:
    """Cortex Auth0 login page."""

    def __init__(self, page: Page, base_url: str, tenant_code: str):
        self.page = page
        self.base_url = base_url
        self.tenant_code = tenant_code

    def navigate(self):
        self.page.goto(f"{self.base_url}/login?tenantCode={self.tenant_code}")

    def click_sign_in_with_google(self):
        self.page.get_by_text("Sign in with Google").click()
