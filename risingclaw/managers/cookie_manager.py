from selenium import webdriver
from pickle import load, dump
from os import path
from ..utilities.logger import time_print
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait



class CookieManager:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.cookies_path = "data/cookie.pkl"

    def save_cookies(self):
        time_print("Saving cookies")
        with open(self.cookies_path, "wb") as file:
            dump(self.driver.get_cookies(), file)

    def load_cookies(self):
        time_print("Loading cookies")
        if path.exists(self.cookies_path):
            self.driver.get("https://risinghub.net")
            with open(self.cookies_path, "rb") as file:
                cookies = load(file)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
            sleep(1)
            #For some reason requires 2 refreshes for the cookies to load properly.
            self.driver.refresh()
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script('return document.readyState') == 'complete')
            self.driver.refresh()
            return True
        return False
