from os import getenv
from ..utilities.logger import time_print
from ..managers.excel_manager import ExcelManager


class SetupChecks:
    def __init__(self):
        self.excel_manager = ExcelManager()

    def do_env_login_variables_exist(self):
        time_print("Checking if environment variables exist")
        if getenv("USERNAME") and getenv("PASSWORD"):
            time_print("Environment variables exist")
        else:
            time_print("Environment variables do not exist")
            time_print("Please enter username and password in .env file")
            exit(0)

    def check_excel_file(self):
        time_print("Checking if Excel log file exists and is initialized")
        self.excel_manager.ensure_excel_file_exists()
