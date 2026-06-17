import sys
import traceback

from dotenv import load_dotenv

load_dotenv(verbose=True, override=True)

from .checks.setup_checks import SetupChecks
from .errors import AlreadyRanError, ClawError
from .operations.claw_runner import ClawRunner
from .services.discord_notifier import DiscordNotifier
from .utilities.logger import time_print


def _notify_error(notifier: DiscordNotifier, exc: BaseException) -> None:
    message = str(exc).strip() or exc.__class__.__name__
    if not isinstance(exc, ClawError):
        trace = traceback.format_exc().strip()
        if trace:
            message = f"{message}\n\n{trace}"
    notifier.notify_error(message)


if __name__ == "__main__":
    notifier = DiscordNotifier.from_config()
    try:
        time_print("Starting main execution")
        SetupChecks().run()
        result = ClawRunner().run()
        notifier.notify_success(result)
    except AlreadyRanError as exc:
        time_print(str(exc))
        sys.exit(0)
    except ClawError as exc:
        time_print(str(exc))
        _notify_error(notifier, exc)
        sys.exit(1)
    except Exception as exc:
        time_print(f"An error occurred in the main execution. Message: {exc}")
        _notify_error(notifier, exc)
        sys.exit(1)
