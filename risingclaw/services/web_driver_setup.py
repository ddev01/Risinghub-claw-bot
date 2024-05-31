from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from ..utilities.logger import time_print


class WebDriverSetup:
    def __init__(self):
        time_print("Initializing WebDriverSetup")
        self.driver = self.setup_driver()

    def setup_driver(self) -> webdriver.Firefox:
        time_print("Setting up Firefox WebDriver")
        options = Options()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.binary_location = '/opt/firefox-128.0a1/firefox'
        service = Service(executable_path='/usr/local/bin/geckodriver')
        return webdriver.Firefox(service=service, options=options)
