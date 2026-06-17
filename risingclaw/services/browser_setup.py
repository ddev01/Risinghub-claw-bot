from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from ..config import AppConfig, load_config
from ..errors import BrowserError
from ..utilities.logger import time_print


class BrowserSession:
    def __init__(self, app_config: AppConfig | None = None):
        self.config = app_config or load_config()
        self._playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None

    def start(self, storage_state: str | None = None) -> tuple[Browser, BrowserContext, Page]:
        time_print("Starting Playwright browser")
        if self.config.browser != "chromium":
            raise BrowserError(f"Unsupported browser: {self.config.browser}")

        self._playwright = sync_playwright().start()
        self.browser = self._playwright.chromium.launch(headless=self.config.headless)
        context_options: dict[str, str] = {}
        if storage_state is not None:
            time_print("Loading cookies")
            context_options["storage_state"] = storage_state
        self.context = self.browser.new_context(**context_options)
        self.page = self.context.new_page()
        return self.browser, self.context, self.page

    def stop(self) -> None:
        time_print("Stopping Playwright browser")
        if self.context:
            self.context.close()
            self.context = None
        if self.browser:
            self.browser.close()
            self.browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None
        self.page = None
