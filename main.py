from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
from dotenv import load_dotenv
import pickle
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import datetime
from time import sleep

# Load environment variables
load_dotenv()

def log_with_timestamp(message: str):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")


class WebDriverSetup:
    def __init__(self):
        log_with_timestamp("Initializing WebDriverSetup")
        self.driver = self.setup_driver()

    def setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome WebDriver with specified options."""
        log_with_timestamp("Setting up Chrome WebDriver")
        options = Options()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-images")  # Disable images
        options.add_experimental_option(
            "prefs",
            {
                "profile.default_content_setting_values.images": 2,
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_settings.cookies": 2,  # Automatically accept cookies
            },
        )
        service = Service(executable_path="/opt/homebrew/bin/chromedriver")        return webdriver.Chrome(service=service, options=options)


class Auth:
    def __init__(self, driver):
        log_with_timestamp("Initializing Auth")
        self.driver = driver
        self.env_user, self.env_password = self.load_env()

    @staticmethod
    def load_env():
        """Load environment variables and return username and password."""
        log_with_timestamp("Loading environment variables")
        env_user = os.getenv("USERNAME")
        env_password = os.getenv("PASSWORD")        return env_user, env_password

    def load_cookies(self):
        """Load cookies from a file."""
        log_with_timestamp("Loading cookies from file")
        if os.path.exists("cookie.pkl"):
            self.driver.get("https://risinghub.net")
            try:
                cookies = pickle.load(open("cookie.pkl", "rb"))
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                self.driver.execute_script("window.location.reload();")
                return True
            except Exception as e:
                log_with_timestamp(f"Failed to load cookies. Message: {e}")
                return False
        else:
            log_with_timestamp("Cookies do not exist")
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

    def check_login_status(self, redir=True) -> bool:
        """Check the login status by looking for the profile link in the navbar."""
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
            log_with_timestamp("Logged in!")            return True
        except NoSuchElementException as e:
            log_with_timestamp(f"Not logged in or element not found. Message: {e.msg}")            return False
        except TimeoutException as e:
            log_with_timestamp(f"Timeout while checking login status. Message: {e.msg}")            return False

    def login(self):
        """Perform login action using environment credentials and check for login errors."""
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
        finally:
    def save_cookies(self):
        """Save cookies to a file after successful login."""
        log_with_timestamp("Saving cookies to file")
        try:
            pickle.dump(self.driver.get_cookies(), open("cookie.pkl", "wb"))
        except Exception as e:
            log_with_timestamp(f"Error while saving cookies. Message: {e.msg}")
    def accept_consent(self):
        """Accept consent on the webpage."""
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
        except Exception as e:
            log_with_timestamp(
                f"An error occurred while accepting consent. Message: {e}"
            )

class SeleniumChecks:
    def __init__(self):
        log_with_timestamp("Initializing SeleniumChecks")
        self.web_driver_setup = WebDriverSetup()
        self.auth = Auth(self.web_driver_setup.driver)

    def run_check(self):
        log_with_timestamp("Running Selenium checks")
        try:
            if not self.auth.load_cookies():
                self.auth.login()
                if self.auth.check_login_status(redir=False):
                    self.auth.save_cookies()
                    self.auth.driver.get(
                        "https://risinghub.net/roulette"
                    )  
                else:
                    self.auth.check_wrong_login()
            else:
                if not self.auth.check_login_status():
                    self.auth.login()
                    self.auth.save_cookies()
        except Exception as e:
            log_with_timestamp(f"An error occurred during the check. Message: {e}")
        input("finish?")


class SetupChecks:
    def __init__(self):
        log_with_timestamp("Initializing SetupChecks")

    def do_env_login_variables_exist(self):
        """Check if environment variables exist."""
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