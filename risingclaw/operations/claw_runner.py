from playwright.sync_api import Page

from ..account import AccountConfig
from ..checks.login_checker import LoginChecker
from ..config import AppConfig
from ..errors import ClawError
from ..managers.cookie_manager import CookieManager
from ..managers.prize_log import PrizeLog
from ..operations.claw import Claw
from ..prize_result import PrizeResult
from ..services.authentication import Authentication
from ..services.browser_setup import BrowserSession
from ..utilities.debug_artifacts import save_failure_artifacts
from ..utilities.logger import time_print


class ClawRunner:
    def __init__(self, app_config: AppConfig, account: AccountConfig):
        time_print(f"Initializing ClawRunner for [{account.id}]")
        self.app_config = app_config
        self.account = account

        self.session = BrowserSession(app_config)
        self.prize_log = PrizeLog(account)
        self.cookie_manager = CookieManager(account)
        self.page: Page | None = None

    def run(self) -> PrizeResult:
        time_print(f"Running claw automation for [{self.account.id}]")
        try:
            storage_state = self.cookie_manager.storage_state_path
            _, context, page = self.session.start(storage_state=storage_state)
            self.page = page

            if storage_state is not None:
                page.goto(self.app_config.base_url)
                page.wait_for_load_state("domcontentloaded")

            auth = Authentication(page, self.account)
            login_checker = LoginChecker(page, self.account)
            claw = Claw(page, self.prize_log, self.account)

            logged_in = login_checker.check_login_status() if storage_state else False
            if not logged_in:
                auth.login()
                if not login_checker.check_login_status():
                    login_checker.check_wrong_login()
                    raise ClawError("Login failed without a visible error message.")
                self.cookie_manager.save(context)

            return self._execute_claw(claw)
        except ClawError:
            raise
        except Exception as exc:
            if self.page:
                save_failure_artifacts(self.page, "runner-error", self.account)
            raise ClawError(f"Claw automation failed: {exc}") from exc
        finally:
            self.session.stop()

    def _execute_claw(self, claw: Claw) -> PrizeResult:
        time_print("Executing Claw operations")
        hero = claw.pick_hero()
        return claw.claim_prize(hero)
