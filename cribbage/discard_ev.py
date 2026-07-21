"""Exact expected-value discard evaluation.

For a dealt hand, evaluate each possible discard by the *exact* expected show
value of the retained 4 cards, averaged over every possible starter drawn from
the unseen cards. This is the tractable, provably-correct baseline discussed in
the design notes: it optimizes expected hand points against a random starter and
ignores (for now) crib contribution and win-probability weighting.

Extending this toward optimality means adding: (1) expected crib value given an
opponent discard model, and (2) reweighting points by P(reaching 121 first)
using board position. Both are good exercises to build on top of this.
"""

from __future__ import annotations
from itertools import combinations
from functools import lru_cache

from .cards import Card, make_deck
from .scoring import score_hand


@lru_cache(maxsize=None)
def _cached_discard_evs(hand_key: tuple, seen_key: tuple):
    hand = [Card(*t) for t in hand_key]
    seen = [Card(*t) for t in seen_key]
    seen_set = set(hand) | set(seen)
    unseen = [c for c in make_deck() if c not in seen_set]
    results = []
    for kept in combinations(hand, 4):
        kept = list(kept)
        discarded = next(c for c in hand if c not in kept)
        ev = sum(score_hand(kept, starter) for starter in unseen) / len(unseen)
        results.append((ev, kept, discarded))
    results.sort(key=lambda t: t[0], reverse=True)
    return results


def discard_evs(hand: list[Card], seen: list[Card] | None = None) -> list[tuple[float, list[Card], Card]]:
    """Return (expected_value, kept_4_cards, discarded_card) sorted best-first.

    In three-handed cribbage each player keeps 4 of 5 dealt cards, so there are
    exactly 5 candidate discards. Results are cached by hand (and seen cards).
    """
    seen = list(seen or [])
    hand_key = tuple(sorted((c.rank, c.suit) for c in hand))
    seen_key = tuple(sorted((c.rank, c.suit) for c in seen))
    return _cached_discard_evs(hand_key, seen_key)


def best_discard(hand: list[Card], seen: list[Card] | None = None) -> tuple[list[Card], Card]:
    _, kept, discarded = discard_evs(hand, seen)[0]
    return kept, discarded
