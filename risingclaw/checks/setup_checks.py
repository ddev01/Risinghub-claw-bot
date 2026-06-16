from ..config import load_config
from ..errors import ClawError
from ..managers.prize_log import PrizeLog
from ..utilities.logger import time_print


class SetupChecks:
    def __init__(self):
        try:
            self.config = load_config()
        except ValueError as exc:
            raise ClawError(str(exc)) from exc
        self.prize_log = PrizeLog(self.config)

    def run(self) -> None:
        self.do_env_login_variables_exist()
        self.check_prize_log()

    def do_env_login_variables_exist(self) -> None:
        time_print("Checking if environment variables exist")
        if self.config.username and self.config.password and self.config.base_url:
            time_print("Environment variables exist")
            return
        raise ClawError("Please set BASE_URL, USERNAME, and PASSWORD in the .env file.")

    def check_prize_log(self) -> None:
        time_print("Checking if prize log exists and is initialized")
        self.prize_log.ensure_exists()
