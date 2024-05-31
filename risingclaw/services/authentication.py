from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from os import getenv
from ..utilities.logger import time_print
from ..services.hide_stuff import hide_stuff



class Authentication:
    def __init__(self, driver):
        time_print("Initializing Authentication")
        self.driver = driver
        self.env_user, self.env_password = self.load_env()

    @staticmethod
    def load_env():
        time_print("Loading environment variables")
        return getenv("USERNAME"), getenv("PASSWORD")

    def login(self):
        time_print("Performing login")
        self.driver.get("https://risinghub.net/login")
        hide_stuff(self.driver)
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
            time_print(f"Timeout during login. Message: {e.msg}")
            self.driver.quit()
            exit(1)

    def accept_consent(self):
        time_print("Accepting consent on the webpage")
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
            time_print(f"Consent button not found or not clickable. Message: {e.msg}")
