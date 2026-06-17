from dataclasses import dataclass


@dataclass(frozen=True)
class PrizeResult:
    account_id: str
    hero: str
    prize: str
    quantity: str
