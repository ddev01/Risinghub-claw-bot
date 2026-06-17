import json
from os import makedirs
from os.path import exists

from ..account import AccountConfig
from ..utilities.logger import time_print


def _accounts_path(app_config) -> str:
    path = getattr(app_config, "accounts_path", None)
    if path:
        return path
    return f"{app_config.data_dir}/accounts.json"


def _require_str(entry: dict, field: str, source: str, index: int) -> str:
    value = entry.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"Account at index {index} in '{source}' requires a non-empty '{field}'."
        )
    return value.strip()


def _parse_heroes(raw, source: str, index: int) -> list[str] | None:
    if raw is None or raw == "":
        return None
    if not isinstance(raw, list):
        raise ValueError(
            f"Account at index {index} in '{source}' must have 'heroes' as a list or null."
        )
    heroes: list[str] = []
    for hero_index, hero in enumerate(raw):
        if not isinstance(hero, str) or not hero.strip():
            raise ValueError(
                f"Account at index {index} in '{source}' has invalid hero at index {hero_index}."
            )
        heroes.append(hero.strip())
    return heroes


def _parse_account(entry: dict, app_config, source: str, index: int) -> AccountConfig:
    if not isinstance(entry, dict):
        raise ValueError(f"Account at index {index} in '{source}' must be a JSON object.")

    return AccountConfig(
        id=_require_str(entry, "id", source, index),
        username=_require_str(entry, "username", source, index),
        password=_require_str(entry, "password", source, index),
        heroes=_parse_heroes(entry.get("heroes"), source, index),
        base_url=app_config.base_url,
        app_data_dir=app_config.data_dir,
    )


def load_accounts(app_config) -> list[AccountConfig]:
    path = _accounts_path(app_config)

    if not exists(path):
        time_print(
            f"WARNING: accounts file not found at '{path}'. "
            "Copy accounts.example.json to that path and fill in credentials; "
            "account credentials are not loaded from .env."
        )
        return []

    with open(path, encoding="utf-8") as file:
        raw = json.load(file)

    if not isinstance(raw, list):
        raise ValueError(f"Expected a JSON array in '{path}'.")

    if not raw:
        raise ValueError(f"Accounts file '{path}' must contain at least one account.")

    accounts: list[AccountConfig] = []
    seen_ids: set[str] = set()

    for index, entry in enumerate(raw):
        account = _parse_account(entry, app_config, path, index)
        if account.id in seen_ids:
            raise ValueError(f"Duplicate account id '{account.id}' in '{path}'.")
        seen_ids.add(account.id)
        accounts.append(account)

    return accounts


def ensure_account_dirs(account: AccountConfig) -> None:
    makedirs(account.data_dir, exist_ok=True)
    makedirs(account.debug_dir, exist_ok=True)
