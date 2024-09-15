from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from ..utilities.logger import time_print


class LoginChecker:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def check_login_status(self):
        time_print("Checking login status")
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "main-nav"))
            )
            self.driver.find_element(
                By.XPATH,
                "//nav[@id='main-nav']//a[@href='https://risinghub.net/profile']",
            )
            time_print("Logged in!")
            return True
        except Exception as e:
            time_print(f"Login status check failed. Message: {e}")
            return False

    def check_wrong_login(self):
        time_print("Checking for login errors")
        try:
            # Wait for the error message to be visible up to 3 seconds
            error_message_element = WebDriverWait(self.driver, 3).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert.callout p"))
            )
            error_message = error_message_element.text
            if error_message:
                time_print(f"Login error detected: {error_message}")
                return True
        except TimeoutException:
            time_print("No login error message found within 3 seconds.")
        finally:
            self.driver.quit()
        return False
