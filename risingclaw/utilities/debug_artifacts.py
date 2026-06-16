from datetime import datetime
from os.path import join

from playwright.sync_api import Page

from ..config import load_config
from ..utilities.logger import time_print


def save_failure_artifacts(page: Page, label: str) -> None:
    config = load_config()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    base_name = f"{timestamp}-{label}"
    png_path = join(config.debug_dir, f"{base_name}.png")
    html_path = join(config.debug_dir, f"{base_name}.html")

    try:
        page.screenshot(path=png_path, full_page=True)
        with open(html_path, "w", encoding="utf-8") as file:
            file.write(page.content())
        time_print(f"Saved debug artifacts: {png_path}, {html_path}")
    except Exception as exc:
        time_print(f"Failed to save debug artifacts: {exc}")
