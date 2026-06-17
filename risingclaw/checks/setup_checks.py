from ..config import AppConfig, load_config
from ..errors import ClawError
from ..managers.account_store import ensure_account_dirs, load_accounts
from ..managers.prize_log import PrizeLog
from ..utilities.logger import time_print


class SetupChecks:
    def __init__(self):
        try:
            self.config: AppConfig = load_config()
        except ValueError as exc:
            raise ClawError(str(exc)) from exc

    def run(self) -> None:
        accounts = self.check_accounts()
        self.check_prize_logs(accounts)

    def check_accounts(self):
        time_print("Checking accounts configuration")
        try:
            accounts = load_accounts(self.config)
        except ValueError as exc:
            raise ClawError(str(exc)) from exc

        if not accounts:
            raise ClawError(
                f"Missing or empty accounts file at '{self.config.accounts_path}'. "
                "Copy accounts.example.json and configure at least one account."
            )

        for account in accounts:
            ensure_account_dirs(account)

        time_print(f"Loaded {len(accounts)} account(s)")
        return accounts

    def check_prize_logs(self, accounts) -> None:
        time_print("Checking if prize logs exist and are initialized")
        for account in accounts:
            PrizeLog(account).ensure_exists()
