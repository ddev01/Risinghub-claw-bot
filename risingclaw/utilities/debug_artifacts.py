from datetime import datetime
from os import makedirs
from os.path import join

from playwright.sync_api import Page

from ..account import AccountConfig
from ..config import load_config
from ..utilities.logger import time_print


def save_failure_artifacts(
    page: Page,
    label: str,
    account: AccountConfig | None = None,
) -> None:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    if account is not None:
        debug_dir = account.debug_dir
        base_name = f"{account.id}-{timestamp}-{label}"
    else:
        config = load_config()
        debug_dir = f"{config.data_dir}/debug"
        base_name = f"{timestamp}-{label}"

    makedirs(debug_dir, exist_ok=True)
    png_path = join(debug_dir, f"{base_name}.png")
    html_path = join(debug_dir, f"{base_name}.html")

    try:
        page.screenshot(path=png_path, full_page=True)
        with open(html_path, "w", encoding="utf-8") as file:
            file.write(page.content())
        time_print(f"Saved debug artifacts: {png_path}, {html_path}")
    except Exception as exc:
        time_print(f"Failed to save debug artifacts: {exc}")
