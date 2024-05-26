from ..services.web_driver_setup import WebDriverSetup
from ..services.authentication import Authentication
from ..managers.cookie_manager import CookieManager
from ..checks.login_checker import LoginChecker
from ..managers.excel_manager import ExcelManager
from ..operations.claw import Claw
from ..utilities.logger import time_print
from ..checks.already_ran import has_already_run


class SeleniumChecks:
    def __init__(self):
        time_print("Initializing SeleniumChecks")
        if has_already_run():
            time_print("Script already ran today. Exiting.")
            exit(1)
        self.web_driver_setup = WebDriverSetup()
        self.auth = Authentication(self.web_driver_setup.driver)
        self.cookie_manager = CookieManager(self.web_driver_setup.driver)
        self.login_checker = LoginChecker(self.web_driver_setup.driver)
        self.excel_manager = ExcelManager()
        self.claw = Claw(self.web_driver_setup.driver, self.excel_manager)

    def run_check(self):
        time_print("Running Selenium checks")
        if self.cookie_manager.load_cookies():
            if not self.login_checker.check_login_status():
                self.auth.login()
                self.cookie_manager.save_cookies()
            self.execute_claw()  # Execute Claw if cookies are loaded and login status is valid
        else:
            self.auth.login()
            if self.login_checker.check_login_status():
                self.cookie_manager.save_cookies()
                self.execute_claw()  # Execute Claw after successful login and cookie save
            else:
                self.login_checker.check_wrong_login()

    def execute_claw(self):
        time_print("Executing Claw operations")
        hero = self.claw.pick_hero()
        self.claw.claim_prize(hero)
