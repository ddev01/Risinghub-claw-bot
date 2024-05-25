from datetime import datetime


def time_print(message: str):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")
