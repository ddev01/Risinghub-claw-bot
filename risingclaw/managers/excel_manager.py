import pandas as pd
from os import path, makedirs
from datetime import datetime
from ..utilities.logger import time_print


class ExcelManager:
    def __init__(self, filename="log.xlsx", directory="data"):
        self.directory = directory
        self.filename = path.join(self.directory, filename)
        self.headers = ["date", "time", "hero", "prize", "quantity"]
        self.ensure_directory_exists()

    def ensure_directory_exists(self):
        """Ensure that the directory for the Excel file exists."""
        if not path.exists(self.directory):
            makedirs(self.directory)
            time_print(f"Created directory '{self.directory}'.")

    def log_to_excel(self, hero, prize, quantity):
        now = datetime.now()
        data = {
            "date": [now.strftime("%Y-%m-%d")],  # Ensure date is in string format
            "time": [now.strftime("%H:%M:%S")],
            "hero": [hero],
            "prize": [prize],
            "quantity": [quantity],
        }

        if not path.exists(self.filename):
            df = pd.DataFrame(columns=self.headers)
        else:
            df = pd.read_excel(self.filename)

        new_df = pd.DataFrame(data)
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_excel(self.filename, index=False)

    def read_last_prize(self) -> dict:
        df = pd.read_excel(
            self.filename, parse_dates=["date"]
        )  # Parse 'date' as datetime object
        if not df.empty and "hero" and "prize" in df.columns:
            last_entry = {
                "date": df.iloc[-1]["date"].strftime(
                    "%Y-%m-%d"
                ),  # Convert datetime to string
                "time": df.iloc[-1]["time"],
                "hero": df.iloc[-1]["hero"],
                "prize": df.iloc[-1]["prize"],
                "quantity": df.iloc[-1]["quantity"],
            }
            return last_entry
        else:
            return None  # Excel file exists but is empty or missing 'hero' column

    def ensure_excel_file_exists(self):
        if not path.exists(self.filename):
            # Create an empty DataFrame with headers and save it
            df = pd.DataFrame(columns=self.headers)
            df.to_excel(self.filename, index=False)
            time_print(f"Created new Excel file '{self.filename}' with headers.")
