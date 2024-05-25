from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        error_message = self.driver.find_element(By.ID, "error_message").text
        if error_message:
            time_print(f"Login error detected: {error_message}")
            return True
        return False
