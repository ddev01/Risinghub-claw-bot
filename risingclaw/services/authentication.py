from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from ..account import AccountConfig
from ..errors import LoginError
from ..services.hide_stuff import hide_stuff
from ..utilities.debug_artifacts import save_failure_artifacts
from ..utilities.logger import time_print


class Authentication:
    def __init__(self, page: Page, account: AccountConfig):
        time_print("Initializing Authentication")
        self.page = page
        self.account = account

    def login(self) -> None:
        time_print("Performing login")
        try:
            self.page.goto(self.account.login_url)
            hide_stuff(self.page)
            # self.accept_consent()  # popup removed for now; keep method below

            username_field = self.page.locator('input[name="username"]')
            password_field = self.page.locator('input[name="password"]')
            username_field.wait_for(state="visible", timeout=10_000)

            username_field.fill(self.account.username)
            password_field.fill(self.account.password)

            submit_button = self.page.locator(
                'button[name="submit"], input[name="submit"], form button[type="submit"]'
            )
            submit_button.first.click(timeout=10_000)
            self.page.wait_for_load_state("domcontentloaded")
        except PlaywrightTimeoutError as exc:
            save_failure_artifacts(self.page, "login-timeout", self.account)
            raise LoginError(f"Timeout during login: {exc}") from exc
        except Exception as exc:
            save_failure_artifacts(self.page, "login-error", self.account)
            raise LoginError(f"Login failed: {exc}") from exc

    def accept_consent(self) -> None:
        time_print("Accepting consent on the webpage")
        try:
            self.page.locator(
                "p.fc-button-label",
                has_text="Consent",
            ).click(timeout=10_000)
        except PlaywrightTimeoutError as exc:
            time_print(f"Consent button not found or not clickable. Message: {exc}")
