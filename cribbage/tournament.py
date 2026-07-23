"""Monte Carlo tournament harness + the luck-vs-skill measurement.

This is the instrument that answers "how much is luck vs skill": it does not
assume a number, it measures the win-rate edge of a stronger agent and shows how
that edge concentrates as you aggregate more games.
"""

from __future__ import annotations
import math
import random
from collections import Counter

from .game import play_game


def win_rate_stats(wins: int, n_games: int, expected: float = 1 / 3) -> dict:
    """Significance of an observed win count against a fair-share baseline.

    Null hypothesis: no skill edge, so `wins` ~ Binomial(n_games, expected).
    The standard error of the win-rate estimate shrinks as 1/sqrt(n_games), so
    a fixed-size deviation from `expected` becomes more significant (larger z,
    smaller p) purely by playing more games, even with no rule changes. `z` is
    how many standard errors the observed rate sits from `expected`; `p_value`
    is the two-tailed normal-approximation p-value for that z.
    """
    observed = wins / n_games
    se = math.sqrt(expected * (1 - expected) / n_games)
    z = (observed - expected) / se
    p_value = math.erfc(abs(z) / math.sqrt(2))
    return {
        "wins": wins,
        "n_games": n_games,
        "observed": observed,
        "expected": expected,
        "se": se,
        "z": z,
        "p_value": p_value,
    }


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


def win_rate_edge_report(strong, field, n_games=2000, seed=0) -> dict:
    """Like `win_rate_edge`, but also returns significance stats (see
    `win_rate_stats`) so you can judge whether the edge is real or noise."""
    agents = [strong, field, field] if not isinstance(field, list) else [strong] + field
    wins = run_tournament(agents, n_games, seed)
    return win_rate_stats(wins[0], n_games)
