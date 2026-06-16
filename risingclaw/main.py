import sys

from dotenv import load_dotenv

load_dotenv(verbose=True, override=True)

from .checks.setup_checks import SetupChecks
from .errors import AlreadyRanError, ClawError
from .operations.claw_runner import ClawRunner
from .utilities.logger import time_print

if __name__ == "__main__":
    try:
        time_print("Starting main execution")
        SetupChecks().run()
        ClawRunner().run()
    except AlreadyRanError as exc:
        time_print(str(exc))
        sys.exit(0)
    except ClawError as exc:
        time_print(str(exc))
        sys.exit(1)
    except Exception as exc:
        time_print(f"An error occurred in the main execution. Message: {exc}")
        sys.exit(1)
