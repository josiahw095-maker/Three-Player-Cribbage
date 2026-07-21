"""Pegging-phase (the "play") scoring.

`peg_points` scores the event of playing one more card onto the current pile,
given the cards played since the last count reset. Handles 15, 31, pairs/tuples,
and runs. "Go" and last-card points are handled by the game loop, not here.
"""

from __future__ import annotations
from collections import Counter

from .cards import Card


def peg_points(pile: list[Card], count: int) -> int:
    """Points scored by the most recent card that brought the pile to `count`."""
    pts = 0
    if count == 15:
        pts += 2
    if count == 31:
        pts += 2

    # Pairs / tuples: trailing cards of equal rank.
    last_rank = pile[-1].rank
    same = 0
    for c in reversed(pile):
        if c.rank == last_rank:
            same += 1
        else:
            break
    if same >= 2:
        pts += 2 * (same * (same - 1) // 2)

    # Runs: longest trailing window (>=3) whose ranks form a consecutive set.
    for window in range(len(pile), 2, -1):
        chunk = pile[-window:]
        ranks = [c.rank for c in chunk]
        if len(set(ranks)) == len(ranks) and max(ranks) - min(ranks) == len(ranks) - 1:
            pts += window
            break
    return pts
