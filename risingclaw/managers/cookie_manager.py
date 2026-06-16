from os.path import exists

from playwright.sync_api import Browser, BrowserContext

from ..config import Config, load_config
from ..utilities.logger import time_print


class CookieManager:
    def __init__(self, config: Config | None = None):
        self.config = config or load_config()
        self.cookies_path = self.config.cookies_path

    def has_cookies(self) -> bool:
        return exists(self.cookies_path)

    def save(self, context: BrowserContext) -> None:
        time_print("Saving cookies")
        context.storage_state(path=self.cookies_path)

    def load_context(self, browser: Browser) -> BrowserContext:
        time_print("Loading cookies")
        return browser.new_context(storage_state=self.cookies_path)
