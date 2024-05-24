from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from os import getenv, path
from dotenv import load_dotenv
from pickle import load, dump
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import datetime

load_dotenv()

def log_with_timestamp(message: str):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")


class WebDriverSetup:
    def __init__(self):
        log_with_timestamp("Initializing WebDriverSetup")
        self.driver = self.setup_driver()

    def setup_driver(self) -> webdriver.Chrome:
        log_with_timestamp("Setting up Chrome WebDriver")
        options = Options()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-images")
        options.add_experimental_option(
            "prefs",
            {
                "profile.default_content_setting_values.images": 2,
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_settings.cookies": 2,
            },
        )
        service = Service(executable_path="/opt/homebrew/bin/chromedriver")
        return webdriver.Chrome(service=service, options=options)


class Authentication:
    def __init__(self, driver):
        log_with_timestamp("Initializing Authentication")
        self.driver = driver
        self.env_user, self.env_password = self.load_env()

    @staticmethod
    def load_env():
        log_with_timestamp("Loading environment variables")
        return os.getenv("USERNAME"), os.getenv("PASSWORD")

    def login(self):
        log_with_timestamp("Performing login")
        self.driver.get("https://risinghub.net/login")
        self.accept_consent()
        try:
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "submit"))
            )
            username_field.send_keys(self.env_user)
            password_field.send_keys(self.env_password)
            submit_button.click()
        except TimeoutException as e:
            log_with_timestamp(f"Timeout during login. Message: {e.msg}")
            self.driver.quit()
            exit(1)

    def accept_consent(self):
        log_with_timestamp("Accepting consent on the webpage")
        try:
            consent_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//p[@class='fc-button-label' and contains(text(), 'Consent')]",
                    )
                )
            )
            consent_button.click()
        except TimeoutException as e:
            log_with_timestamp(
                f"Consent button not found or not clickable. Message: {e.msg}"
            )


class CookieManager:
    def __init__(self, driver):
        self.driver = driver

    def load_cookies(self):
        log_with_timestamp("Loading cookies from file")
        if os.path.exists("cookie.pkl"):
            self.driver.get("https://risinghub.net")
            try:
                cookies = pickle.load(open("cookie.pkl", "rb"))
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                self.driver.refresh()
                return True
            except Exception as e:
                log_with_timestamp(f"Failed to load cookies. Message: {e}")
                return False
        else:
            log_with_timestamp("Cookies do not exist")
            return False

    def save_cookies(self):
        log_with_timestamp("Saving cookies to file")
        try:
            pickle.dump(self.driver.get_cookies(), open("cookie.pkl", "wb"))
        except Exception as e:
            log_with_timestamp(f"Error while saving cookies. Message: {e}")


class LoginChecker:
    def __init__(self, driver):
        self.driver = driver

    def check_login_status(self, redir=True) -> bool:
        log_with_timestamp("Checking login status")
        if redir:
            self.driver.get("https://risinghub.net/roulette")
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "main-nav"))
            )
            self.driver.find_element(
                By.XPATH,
                "//nav[@id='main-nav']//a[@href='https://risinghub.net/profile']",
            )
            log_with_timestamp("Logged in!")
            return True
        except (NoSuchElementException, TimeoutException):
            log_with_timestamp("Not logged in or element not found.")
            return False

    def check_wrong_login(self):
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".alert.callout"))
            )
            error_message = self.driver.find_element(
                By.CSS_SELECTOR, ".alert.callout p"
            ).text
            if "These credentials do not match our records" in error_message:
                log_with_timestamp("Login failed: Incorrect credentials.")
                log_with_timestamp(
                    "Please check your username and password in .env file"
                )
                self.driver.quit()
                exit(1)
            else:
                log_with_timestamp("Login error with unexpected message.")
                self.driver.quit()
                exit(1)
        except TimeoutException as e:
            log_with_timestamp(
                f"Timeout during login or no error message found. Message: {e.msg}"
            )
            return True
        except NoSuchElementException:
            log_with_timestamp("Logged in successfully.")
            return True


class SeleniumChecks:
    def __init__(self):
        log_with_timestamp("Initializing SeleniumChecks")
        self.web_driver_setup = WebDriverSetup()
        self.auth = Authentication(self.web_driver_setup.driver)
        self.cookie_manager = CookieManager(self.web_driver_setup.driver)
        self.login_checker = LoginChecker(self.web_driver_setup.driver)

    def run_check(self):
        log_with_timestamp("Running Selenium checks")
        if not self.cookie_manager.load_cookies():
            self.auth.login()
            if self.login_checker.check_login_status(redir=False):
                self.cookie_manager.save_cookies()
                self.web_driver_setup.driver.get("https://risinghub.net/roulette")
            else:
                self.login_checker.check_wrong_login()
        else:
            if not self.login_checker.check_login_status():
                self.auth.login()
                self.cookie_manager.save_cookies()


class SetupChecks:
    def __init__(self):
        log_with_timestamp("Initializing SetupChecks")

    def do_env_login_variables_exist(self):
        log_with_timestamp("Checking if environment variables exist")
        if os.getenv("USERNAME") and os.getenv("PASSWORD"):
            log_with_timestamp("Environment variables exist")
        else:
            log_with_timestamp("Environment variables do not exist")
            log_with_timestamp("Please enter username and password in .env file")
            exit(0)


if __name__ == "__main__":
    try:
        log_with_timestamp("Starting main execution")
        setup_checks = SetupChecks()
        setup_checks.do_env_login_variables_exist()
        selenium_checks = SeleniumChecks()
        selenium_checks.run_check()
    except Exception as e:
        log_with_timestamp(f"An error occurred in the main execution. Message: {e}")
