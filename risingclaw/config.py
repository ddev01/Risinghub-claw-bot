from dataclasses import dataclass
from os import getenv, makedirs


def _require(name: str) -> str:
    value = getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def _bool(name: str, default: bool) -> bool:
    raw = getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class AppConfig:
    base_url: str
    headless: bool
    browser: str
    data_dir: str
    timezone: str
    discord_webhook: str | None

    @property
    def accounts_path(self) -> str:
        return f"{self.data_dir}/accounts.json"

    def ensure_data_dir(self) -> None:
        makedirs(self.data_dir, exist_ok=True)


Config = AppConfig


def load_config() -> AppConfig:
    config = AppConfig(
        base_url=_require("BASE_URL").rstrip("/"),
        headless=_bool("HEADLESS", True),
        browser=getenv("BROWSER", "chromium"),
        data_dir=getenv("DATA_DIR", "data"),
        timezone=getenv("TZ", "Europe/Amsterdam"),
        discord_webhook=getenv("DISCORD_WEBHOOK") or None,
    )
    config.ensure_data_dir()
    return config
