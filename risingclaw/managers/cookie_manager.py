from os.path import exists

from playwright.sync_api import BrowserContext

from ..account import AccountConfig
from ..utilities.logger import time_print


class CookieManager:
    def __init__(self, account: AccountConfig):
        self.account = account
        self.cookies_path = account.cookies_path

    def has_cookies(self) -> bool:
        return exists(self.cookies_path)

    @property
    def storage_state_path(self) -> str | None:
        return self.cookies_path if self.has_cookies() else None

    def save(self, context: BrowserContext) -> None:
        time_print("Saving cookies")
        context.storage_state(path=self.cookies_path)
