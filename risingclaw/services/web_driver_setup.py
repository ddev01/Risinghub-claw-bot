from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from ..utilities.logger import time_print


class WebDriverSetup:
    def __init__(self):
        time_print("Initializing WebDriverSetup")
        self.driver = self.setup_driver()

    def setup_driver(self) -> webdriver.Chrome:
        time_print("Setting up Chrome WebDriver")
        options = Options()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        # options.add_argument("--disable-images")
        options.add_experimental_option(
            "prefs",
            {
                # "profile.default_content_setting_values.images": 2,
                # "profile.managed_default_content_settings.images": 2,
                "profile.default_content_settings.cookies": 2,
            },
        )
        service = Service(executable_path="/opt/homebrew/bin/chromedriver")
        return webdriver.Chrome(service=service, options=options)
