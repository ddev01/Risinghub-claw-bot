import pytz
from datetime import datetime, timedelta
from ..managers.excel_manager import ExcelManager


def has_already_run() -> bool:
    """
    Check if the wheel has already been spun after 01:00 AM Amsterdam time today.

    :return: True if already run today after 01:00 AM, False otherwise.
    """
    # Initialize ExcelManager
    excel_manager = ExcelManager()
    last_prize = excel_manager.read_last_prize()

    if last_prize is None:
        return False  # No data logged yet

    # Parse the last run datetime
    last_run_date = datetime.strptime(last_prize["date"], "%Y-%m-%d").date()
    last_run_time = datetime.strptime(last_prize["time"], "%H:%M:%S").time()
    last_run_datetime = datetime.combine(last_run_date, last_run_time)

    # Convert last run datetime to Amsterdam timezone
    amsterdam = pytz.timezone("Europe/Amsterdam")
    last_run_datetime = amsterdam.localize(last_run_datetime)

    # Get the current time in Amsterdam
    now_amsterdam = datetime.now(amsterdam)

    # Calculate the start of the valid period (today at 01:00 AM)
    start_of_day = now_amsterdam.replace(hour=1, minute=0, second=0, microsecond=0)
    if now_amsterdam.hour < 1:
        start_of_day -= timedelta(days=1)  # Go back one day if before 01:00 AM

    # Check if the last run was after today's 01:00 AM
    return last_run_datetime >= start_of_day
