"""Card primitives for cribbage.

Ranks are stored as integers 1..13 (A=1, J=11, Q=12, K=13). This makes run
detection (consecutive ranks) trivial. The *pip value* used for fifteens and
the pegging count is a separate concept: A=1, 2..10 face value, J/Q/K=10.
"""

from __future__ import annotations
from dataclasses import dataclass

SUITS = ("S", "H", "D", "C")
RANK_NAMES = {1: "A", 11: "J", 12: "Q", 13: "K"}


@dataclass(frozen=True, order=True)
class Card:
    rank: int  # 1..13
    suit: str  # one of SUITS

    @property
    def value(self) -> int:
        """Pip value for fifteens and pegging count."""
        return min(self.rank, 10)

    def __str__(self) -> str:
        r = RANK_NAMES.get(self.rank, str(self.rank))
        return f"{r}{self.suit}"

    def __repr__(self) -> str:
        return str(self)


def make_deck() -> list[Card]:
    return [Card(r, s) for s in SUITS for r in range(1, 14)]
