import pyotp
from playwright.sync_api import Page

TIMEOUT = 15000


class GoogleAuthPage:
    """Google OAuth sign-in page with TOTP MFA support.

    Uses dispatch_event("click") instead of click() for Google's buttons
    because macOS passkey/Bluetooth dialogs can steal focus and prevent
    normal Playwright clicks from reaching the page.

    Uses type() instead of fill() for the email field because Google
    detects programmatic fill() and blocks form submission.
    """

    def __init__(self, page: Page, email: str, password: str, totp_uri: str):
        self.page = page
        self.email = email
        self.password = password
        self.totp_uri = totp_uri

    def _js_click(self, locator):
        """Click via JavaScript dispatch to bypass OS-level dialog interference."""
        locator.dispatch_event("click")

    def _wait_for_page_change(self):
        """Wait for Google's SPA page transitions."""
        self.page.wait_for_timeout(2000)

    def _debug_page(self, label: str):
        """Capture screenshot and dump visible interactive elements."""
        self.page.screenshot(path=f"screenshots/debug-{label}.png", full_page=True)
        print(f"\nDEBUG [{label}] title: {self.page.title()}")
        for role in ["link", "button"]:
            for el in self.page.get_by_role(role).all():
                if el.is_visible():
                    print(f"  {role}: '{el.text_content()}'")

    def enter_email(self):
        email_field = self.page.get_by_label("Email or phone")
        email_field.click()
        email_field.type(self.email, delay=50)
        self.page.get_by_role("button", name="Next").click()
        self.page.wait_for_selector("text=Email or phone", state="hidden", timeout=TIMEOUT)

    def dismiss_passkey(self):
        """Dismiss the passkey prompt and navigate to auth method selection."""
        self.page.get_by_role("button", name="Try another way").wait_for(state="visible", timeout=TIMEOUT)
        self._js_click(self.page.get_by_role("button", name="Try another way"))
        self._wait_for_page_change()

    def select_password_method(self):
        """Select 'Enter your password' from the auth method list."""
        password_link = self.page.get_by_text("Enter your password")
        password_link.wait_for(state="visible", timeout=TIMEOUT)
        self._js_click(password_link)
        self._wait_for_page_change()

    def enter_password(self):
        """Fill in password and submit."""
        self.page.get_by_label("Enter your password").wait_for(state="visible", timeout=TIMEOUT)
        self.page.get_by_label("Enter your password").fill(self.password)
        self._js_click(self.page.locator("#passwordNext").get_by_role("button", name="Next"))
        self._wait_for_page_change()

    def dismiss_post_password_passkey(self):
        """Dismiss the second passkey prompt that appears after password entry."""
        try:
            btn = self.page.get_by_role("button", name="Try another way")
            btn.wait_for(state="visible", timeout=5000)
            self._js_click(btn)
            self._wait_for_page_change()
        except Exception:
            # Not every login shows this second prompt — skip if absent
            pass

    def navigate_to_totp(self):
        """From MFA challenge page, select the TOTP option.

        Google labels this differently depending on enrollment method:
        - "Google Authenticator"
        - "Use your phone or tablet to get a security code"
        """
        for label in [
            "Google Authenticator",
            "Use your phone or tablet to get a security code",
        ]:
            totp_option = self.page.get_by_text(label)
            if totp_option.count() > 0:
                totp_option.wait_for(state="visible", timeout=TIMEOUT)
                self._js_click(totp_option)
                self._wait_for_page_change()
                return
        raise Exception("Could not find TOTP option on MFA method selection page")

    def enter_totp(self):
        """Generate and enter TOTP code."""
        totp = pyotp.parse_uri(self.totp_uri)
        code = totp.now()
        self.page.get_by_label("Enter code").wait_for(state="visible", timeout=TIMEOUT)
        self.page.get_by_label("Enter code").fill(code)
        self.page.get_by_label("Enter code").press("Enter")

    def complete_login(self):
        """Run the full Google auth flow:
        email → dismiss passkey → select password → enter password → TOTP
        """
        self.enter_email()
        self.dismiss_passkey()
        self.select_password_method()
        self.enter_password()
        self.dismiss_post_password_passkey()
        self.navigate_to_totp()
        self.enter_totp()
