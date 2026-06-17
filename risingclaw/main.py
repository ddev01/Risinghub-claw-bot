import sys
import traceback

from dotenv import load_dotenv

load_dotenv(verbose=True, override=True)

from .checks.already_ran import has_already_run
from .checks.setup_checks import SetupChecks
from .config import load_config
from .errors import ClawCooldownError, ClawError
from .operations.claw_runner import ClawRunner
from .services.discord_notifier import DiscordNotifier
from .utilities.logger import time_print


def _notify_error(notifier: DiscordNotifier, exc: BaseException | str) -> None:
    message = str(exc).strip() or (exc.__class__.__name__ if isinstance(exc, BaseException) else "Unknown error")
    if not isinstance(exc, ClawError):
        trace = traceback.format_exc().strip()
        if trace:
            message = f"{message}\n\n{trace}"
    notifier.notify_error(message)


if __name__ == "__main__":
    app_config = load_config()
    notifier = DiscordNotifier.from_config(app_config)
    try:
        time_print("Starting main execution")
        accounts = SetupChecks(app_config).run()
        failures: list[str] = []
        for account in accounts:
            if has_already_run(account, app_config.timezone):
                time_print(f"[{account.id}] Already ran today. Skipping.")
                continue
            try:
                result = ClawRunner(app_config, account).run()
                notifier.notify_success(result)
            except ClawCooldownError as exc:
                time_print(f"[{account.id}] {exc}")
            except ClawError as exc:
                failures.append(account.id)
                time_print(f"[{account.id}] {exc}")
                _notify_error(notifier, f"[{account.id}] {exc}")
        sys.exit(1 if failures else 0)
    except ClawError as exc:
        time_print(str(exc))
        _notify_error(notifier, exc)
        sys.exit(1)
    except Exception as exc:
        time_print(f"An error occurred in the main execution. Message: {exc}")
        _notify_error(notifier, exc)
        sys.exit(1)
