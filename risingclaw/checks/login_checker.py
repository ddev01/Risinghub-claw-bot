from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from ..config import Config, load_config
from ..errors import LoginError
from ..utilities.debug_artifacts import save_failure_artifacts
from ..utilities.logger import time_print


class LoginChecker:
    def __init__(self, page: Page, config: Config | None = None):
        self.page = page
        self.config = config or load_config()

    def check_login_status(self) -> bool:
        time_print("Checking login status")
        try:
            self.page.locator("#main-nav").wait_for(timeout=10_000)
            self.page.locator(
                f"nav#main-nav a[href='{self.config.profile_url}']"
            ).first.wait_for(state="visible", timeout=10_000)
            time_print("Logged in!")
            return True
        except PlaywrightTimeoutError as exc:
            time_print(f"Login status check failed. Message: {exc}")
            return False

    def check_wrong_login(self) -> None:
        time_print("Checking for login errors")
        try:
            error_message = self.page.locator(".alert.callout p").inner_text(timeout=3_000)
            if error_message:
                save_failure_artifacts(self.page, "wrong-login")
                raise LoginError(f"Login error detected: {error_message}")
        except PlaywrightTimeoutError:
            time_print("No login error message found within 3 seconds.")
            save_failure_artifacts(self.page, "login-status-unknown")
            raise LoginError("Login failed without a visible error message.")
