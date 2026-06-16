from playwright.sync_api import Page

from ..checks.already_ran import has_already_run
from ..checks.login_checker import LoginChecker
from ..config import Config, load_config
from ..errors import AlreadyRanError, ClawError
from ..managers.cookie_manager import CookieManager
from ..managers.prize_log import PrizeLog
from ..operations.claw import Claw
from ..services.authentication import Authentication
from ..services.browser_setup import BrowserSession
from ..utilities.debug_artifacts import save_failure_artifacts
from ..utilities.logger import time_print


class ClawRunner:
    def __init__(self, config: Config | None = None):
        time_print("Initializing ClawRunner")
        self.config = config or load_config()
        if has_already_run():
            raise AlreadyRanError("Script already ran today. Exiting.")

        self.session = BrowserSession(self.config)
        self.prize_log = PrizeLog(self.config)
        self.cookie_manager = CookieManager(self.config)
        self.page: Page | None = None

    def run(self) -> None:
        time_print("Running claw automation")
        try:
            _, context, page = self.session.start()
            self.page = page

            if self.cookie_manager.has_cookies():
                context.close()
                context = self.cookie_manager.load_context(self.session.browser)
                self.session.context = context
                page = context.new_page()
                self.session.page = page
                self.page = page
                self._prime_cookie_session(page)

            auth = Authentication(page, self.config)
            login_checker = LoginChecker(page, self.config)
            claw = Claw(page, self.prize_log, self.config)

            if self.cookie_manager.has_cookies():
                if not login_checker.check_login_status():
                    auth.login()
                    self.cookie_manager.save(context)
                self._execute_claw(claw)
                return

            auth.login()
            if login_checker.check_login_status():
                self.cookie_manager.save(context)
                self._execute_claw(claw)
                return

            login_checker.check_wrong_login()
        except ClawError:
            raise
        except Exception as exc:
            if self.page:
                save_failure_artifacts(self.page, "runner-error")
            raise ClawError(f"Claw automation failed: {exc}") from exc
        finally:
            self.session.stop()

    def _prime_cookie_session(self, page: Page) -> None:
        page.goto(self.config.base_url)
        page.reload()
        page.wait_for_load_state("domcontentloaded")
        page.reload()
        page.wait_for_load_state("domcontentloaded")

    def _execute_claw(self, claw: Claw) -> None:
        time_print("Executing Claw operations")
        hero = claw.pick_hero()
        claw.claim_prize(hero)
