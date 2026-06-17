from dataclasses import dataclass


@dataclass(frozen=True)
class AccountConfig:
    id: str
    username: str
    password: str
    heroes: list[str] | None
    base_url: str
    app_data_dir: str

    @property
    def data_dir(self) -> str:
        return f"{self.app_data_dir}/accounts/{self.id}"

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
