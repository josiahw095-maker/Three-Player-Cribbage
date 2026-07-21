"""Monte Carlo tournament harness + the luck-vs-skill measurement.

This is the instrument that answers "how much is luck vs skill": it does not
assume a number, it measures the win-rate edge of a stronger agent and shows how
that edge concentrates as you aggregate more games.
"""

from __future__ import annotations
import random
from collections import Counter

from .game import play_game


def run_tournament(agents, n_games: int, seed: int = 0) -> Counter:
    """Play n_games with rotating starting dealer; return win counts by seat.

    Note: seat identity is fixed but the starting dealer rotates each game to
    neutralize the deal advantage over the sample.
    """
    rng = random.Random(seed)
    wins = Counter()
    n = len(agents)
    for g in range(n_games):
        w = play_game(agents, rng=rng, start_dealer=g % n)
        wins[w] += 1
    return wins


def win_rate_edge(strong, field, n_games=2000, seed=0):
    """Win rate of `strong` (seat 0) against two `field` agents (seats 1,2).

    In a fair 3-player game each seat expects 1/3. The excess over 1/3 is the
    measurable skill edge for this matchup.
    """
    agents = [strong, field, field] if not isinstance(field, list) else [strong] + field
    wins = run_tournament(agents, n_games, seed)
    return wins[0] / n_games
