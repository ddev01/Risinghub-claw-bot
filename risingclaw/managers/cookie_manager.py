from selenium import webdriver
from pickle import load, dump
from os import path
from ..utilities.logger import time_print


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
			#For some reason requires 2 refreshes for the cookies to load properly.
            self.driver.refresh()
            self.driver.refresh()
            return True
        return False
