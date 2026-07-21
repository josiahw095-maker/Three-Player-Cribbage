"""Show-phase scoring: the deterministic core of cribbage.

`score_hand` scores a 4-card hand plus the starter (5 cards total) and returns
the point total. This is pure arithmetic with no hidden information, which is
exactly why it can be exhaustively unit-tested (see tests/test_scoring.py).

Everything else in the project is built on top of this being correct.
"""

from __future__ import annotations
from itertools import combinations
from collections import Counter

from .cards import Card


def _score_fifteens(cards: list[Card]) -> int:
    total = 0
    for r in range(2, len(cards) + 1):
        for combo in combinations(cards, r):
            if sum(c.value for c in combo) == 15:
                total += 2
    return total


def _score_pairs(cards: list[Card]) -> int:
    counts = Counter(c.rank for c in cards)
    return sum(2 * (n * (n - 1) // 2) for n in counts.values())


def _score_runs(cards: list[Card]) -> int:
    """Runs of 3+ consecutive ranks. Duplicated ranks multiply the run.

    e.g. 4-5-5-6 -> run length 3 with a doubled 5 -> 3 * 2 = 6 points.
    """
    counts = Counter(c.rank for c in cards)
    ranks = sorted(counts)
    total = 0
    i = 0
    while i < len(ranks):
        j = i
        while j + 1 < len(ranks) and ranks[j + 1] == ranks[j] + 1:
            j += 1
        run_len = j - i + 1
        if run_len >= 3:
            mult = 1
            for k in range(i, j + 1):
                mult *= counts[ranks[k]]
            total += run_len * mult
        i = j + 1
    return total


def _score_flush(hand: list[Card], starter: Card, is_crib: bool) -> int:
    suits = {c.suit for c in hand}
    if len(suits) != 1:
        return 0
    # All four hand cards share a suit.
    if starter.suit in suits:
        return 5
    # A four-card flush counts in a normal hand but NOT in the crib.
    return 0 if is_crib else 4


def _score_nobs(hand: list[Card], starter: Card) -> int:
    for c in hand:
        if c.rank == 11 and c.suit == starter.suit:  # Jack matching starter suit
            return 1
    return 0


def score_hand(hand: list[Card], starter: Card, is_crib: bool = False) -> int:
    """Score a 4-card hand with the given starter card.

    Set is_crib=True when scoring the crib (four-card flushes don't count there).
    """
    all_cards = list(hand) + [starter]
    return (
        _score_fifteens(all_cards)
        + _score_pairs(all_cards)
        + _score_runs(all_cards)
        + _score_flush(hand, starter, is_crib)
        + _score_nobs(hand, starter)
    )
