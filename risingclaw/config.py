from dataclasses import dataclass
from os import getenv, makedirs
from os.path import exists


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
class Config:
    base_url: str
    username: str
    password: str
    heroes: str | None
    headless: bool
    browser: str
    data_dir: str
    timezone: str

    @property
    def login_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/login"

    @property
    def claw_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/claw"

    @property
    def profile_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/profile"

    @property
    def log_path(self) -> str:
        return f"{self.data_dir}/log.json"

    @property
    def cookies_path(self) -> str:
        return f"{self.data_dir}/cookies.json"

    @property
    def heroes_path(self) -> str:
        return f"{self.data_dir}/heroes.json"

    @property
    def debug_dir(self) -> str:
        return f"{self.data_dir}/debug"

    def ensure_data_dir(self) -> None:
        makedirs(self.data_dir, exist_ok=True)
        makedirs(self.debug_dir, exist_ok=True)


def load_config() -> Config:
    config = Config(
        base_url=_require("BASE_URL").rstrip("/"),
        username=_require("USERNAME"),
        password=_require("PASSWORD"),
        heroes=getenv("HEROES"),
        headless=_bool("HEADLESS", True),
        browser=getenv("BROWSER", "chromium"),
        data_dir=getenv("DATA_DIR", "data"),
        timezone=getenv("TZ", "Europe/Amsterdam"),
    )
    config.ensure_data_dir()
    return config
