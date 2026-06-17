from dataclasses import dataclass


@dataclass(frozen=True)
class PrizeResult:
    hero: str
    prize: str
    quantity: str
