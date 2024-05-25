from dotenv import load_dotenv
from os import getenv

# Fix caching issue.
load_dotenv(verbose=True, override=True)

from .operations.selenium_checks import SeleniumChecks
from .utilities.logger import time_print
from .checks.setup_checks import SetupChecks

if __name__ == "__main__":
    try:
        time_print("Starting main execution")
        setup_checks = SetupChecks()
        setup_checks.do_env_login_variables_exist()
        setup_checks.check_excel_file()
        selenium_checks = SeleniumChecks()
        selenium_checks.run_check()
    except Exception as e:
        time_print(f"An error occurred in the main execution. Message: {e}")
