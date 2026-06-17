import json
from datetime import datetime
from os.path import exists

from ..account import AccountConfig
from ..utilities.logger import time_print


class PrizeLog:
    def __init__(self, account: AccountConfig):
        self.account = account
        self.path = account.log_path

    def ensure_exists(self) -> None:
        if not exists(self.path):
            with open(self.path, "w", encoding="utf-8") as file:
                json.dump([], file)
            time_print(f"Created new prize log '{self.path}'.")

    def append(self, hero: str, prize: str, quantity: str) -> None:
        now = datetime.now()
        entry = {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "account": self.account.id,
            "hero": hero,
            "prize": prize,
            "quantity": quantity,
        }

        entries = self._read_all()
        entries.append(entry)
        self._write_all(entries)

    def read_last(self) -> dict | None:
        entries = self._entries_for_account(self._read_all())
        if not entries:
            return None
        return entries[-1]

    def _entries_for_account(self, entries: list[dict]) -> list[dict]:
        return [entry for entry in entries if entry.get("account") == self.account.id]

    def _read_all(self) -> list[dict]:
        if not exists(self.path):
            return []
        with open(self.path, encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError(f"Expected a JSON array in '{self.path}'.")
        return data

    def _write_all(self, entries: list[dict]) -> None:
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(entries, file, indent=2)
