import pytz
from datetime import datetime, timedelta

from ..managers.prize_log import PrizeLog


def has_already_run() -> bool:
    """
    Check if the wheel has already been spun after 01:00 AM Amsterdam time today.

    :return: True if already run today after 01:00 AM, False otherwise.
    """
    prize_log = PrizeLog()
    last_prize = prize_log.read_last()

    if last_prize is None:
        return False

    last_run_date = datetime.strptime(last_prize["date"], "%Y-%m-%d").date()
    last_run_time = datetime.strptime(last_prize["time"], "%H:%M:%S").time()
    last_run_datetime = datetime.combine(last_run_date, last_run_time)

    amsterdam = pytz.timezone("Europe/Amsterdam")
    last_run_datetime = amsterdam.localize(last_run_datetime)

    now_amsterdam = datetime.now(amsterdam)

    start_of_day = now_amsterdam.replace(hour=1, minute=0, second=0, microsecond=0)
    if now_amsterdam.hour < 1:
        start_of_day -= timedelta(days=1)

    return last_run_datetime >= start_of_day
