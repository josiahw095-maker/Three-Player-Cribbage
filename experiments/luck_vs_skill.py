"""Experiment: how a fixed skill edge concentrates with match length.

Core idea: luck-vs-skill is not one number, it's a curve. We pit a slightly
better agent (lower epsilon) against slightly worse ones and measure how often
the better one wins a *match* of K games, as K grows. Short matches ~ coin flip
(luck dominates); long matches ~ the skill edge dominates.

Run:  python experiments/luck_vs_skill.py
"""
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cribbage.agents import NoisyGreedyAgent
from cribbage.game import play_game


def single_game_edge(eps_strong, eps_weak, n_games, seed):
    rng = random.Random(seed)
    strong = NoisyGreedyAgent(eps_strong, rng)
    weak1 = NoisyGreedyAgent(eps_weak, rng)
    weak2 = NoisyGreedyAgent(eps_weak, rng)
    agents = [strong, weak1, weak2]
    wins = 0
    for g in range(n_games):
        if play_game(agents, rng=rng, start_dealer=g % 3) == 0:
            wins += 1
    return wins / n_games


def match_win_prob(eps_strong, eps_weak, games_per_match, n_matches, seed):
    """P(strong wins a best-of / most-games match of length games_per_match)."""
    rng = random.Random(seed)
    strong = NoisyGreedyAgent(eps_strong, rng)
    weak1 = NoisyGreedyAgent(eps_weak, rng)
    weak2 = NoisyGreedyAgent(eps_weak, rng)
    agents = [strong, weak1, weak2]
    match_wins = 0
    g = 0
    for _ in range(n_matches):
        tally = [0, 0, 0]
        for _ in range(games_per_match):
            tally[play_game(agents, rng=rng, start_dealer=g % 3)] += 1
            g += 1
        if tally[0] == max(tally) and tally.count(max(tally)) == 1:
            match_wins += 1
    return match_wins / n_matches


if __name__ == "__main__":
    # Demo sizes kept small so this finishes in seconds. For real estimates,
    # scale n_games into the thousands and n_matches into the hundreds (and
    # consider optimizing the pegging inner loop — see README).
    print("Single-game win rate (fair share = 0.333):")
    print(f"  eps 0.00 vs 0.30 : {single_game_edge(0.0, 0.30, 200, 1):.3f}")
    print(f"  eps 0.00 vs 0.10 : {single_game_edge(0.0, 0.10, 200, 2):.3f}")
    print()
    print("Match win probability, strong(eps=0) vs two weak(eps=0.15):")
    for k in (1, 5):
        p = match_win_prob(0.0, 0.15, k, 20, seed=100 + k)
        print(f"  best-of-{k:>2} games : {p:.3f}")
