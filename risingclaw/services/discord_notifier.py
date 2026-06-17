import json
from datetime import datetime, timezone
from urllib.error import URLError
from urllib.request import Request, urlopen

from ..config import Config, load_config
from ..prize_result import PrizeResult
from ..utilities.logger import time_print


class DiscordNotifier:
    def __init__(self, webhook_url: str | None):
        self.webhook_url = webhook_url

    @classmethod
    def from_config(cls, config: Config | None = None) -> "DiscordNotifier":
        config = config or load_config()
        return cls(config.discord_webhook)

    def notify_success(self, result: PrizeResult) -> None:
        if not self.webhook_url:
            return

        payload = {
            "embeds": [
                {
                    "title": "Daily Claw",
                    "description": "Prize claimed successfully.",
                    "color": 0x57F287,
                    "fields": [
                        {"name": "Hero", "value": result.hero, "inline": True},
                        {"name": "Prize", "value": result.prize, "inline": True},
                        {"name": "Quantity", "value": result.quantity, "inline": True},
                    ],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ]
        }
        self._send(payload)

    def notify_error(self, message: str) -> None:
        if not self.webhook_url:
            return

        description = message.strip() or "Unknown error"
        if len(description) > 3900:
            description = description[:3900] + "..."

        payload = {
            "content": "@everyone",
            "allowed_mentions": {"parse": ["everyone"]},
            "embeds": [
                {
                    "title": "Daily Claw Failed",
                    "description": description,
                    "color": 0xED4245,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }
        self._send(payload)

    def _send(self, payload: dict) -> None:
        try:
            data = json.dumps(payload).encode("utf-8")
            request = Request(
                self.webhook_url,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "RisingClawBot/1.0",
                },
                method="POST",
            )
            with urlopen(request, timeout=15) as response:
                response.read()
        except URLError as exc:
            time_print(f"Failed to send Discord webhook: {exc}")
