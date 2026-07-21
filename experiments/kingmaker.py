"""Experiment: does trailing-player behavior swing the leader's win rate?

This operationalizes the three-player "kingmaker" problem. We compare a leader's
win rate when the two other seats play neutrally vs. when they adopt an implicit
"suppress the current leader" pegging heuristic. A measurable gap is empirical
evidence of an implicit coalition effect that has no analogue in 2-player play.

This is a *skeleton*: the AntiLeaderAgent below is a simple, honest starting
heuristic. Sharpening the definition of "leader" and the suppression policy is
exactly the kind of extension this project is for.

Run:  python experiments/kingmaker.py
"""
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cribbage.agents import GreedyAgent
from cribbage.pegging import peg_points
from cribbage.game import play_game


class AntiLeaderAgent(GreedyAgent):
    """Greedy discard; pegging grabs points, but among point-equal options it
    avoids setting up the current point leader (whoever it is) when this agent
    is itself behind. Uses live board state passed into play()."""

    name = "anti_leader"

    def play(self, legal, pile, count, state=None):
        # Fall back to plain greedy if we have no board view.
        if state is None:
            return super().play(legal, pile, count, state)
        my_seat = getattr(self, "seat", None)
        scores = state.scores
        # If we're not clearly trailing, just play greedy.
        if my_seat is None or scores[my_seat] >= max(scores):
            return super().play(legal, pile, count, state)
        # Prefer immediate points; otherwise play the card least likely to leave
        # the leader an easy pair/15 next (proxy: dump the highest card).
        scored = [(peg_points(pile + [c], count + c.value), c) for c in legal]
        best_pts = max(s for s, _ in scored)
        if best_pts > 0:
            return max((c for s, c in scored if s == best_pts), key=lambda c: c.value)
        return max(legal, key=lambda c: c.value)


def leader_win_rate(anti: bool, n_games=250, seed=0):
    """Win rate of seat 0 (a plain greedy 'leader-ish' seat) when the other two
    seats either play neutral greedy (anti=False) or anti-leader (anti=True)."""
    rng = random.Random(seed)
    if anti:
        others = [AntiLeaderAgent(rng), AntiLeaderAgent(rng)]
    else:
        others = [GreedyAgent(rng), GreedyAgent(rng)]
    for i, a in enumerate(others, start=1):
        a.seat = i
    agents = [GreedyAgent(rng)] + others
    agents[0].seat = 0
    wins = sum(play_game(agents, rng=rng, start_dealer=g % 3) == 0 for g in range(n_games))
    return wins / n_games


if __name__ == "__main__":
    base = leader_win_rate(anti=False, n_games=250, seed=1)
    supp = leader_win_rate(anti=True, n_games=250, seed=1)
    print(f"Seat-0 win rate, neutral opponents : {base:.3f}")
    print(f"Seat-0 win rate, anti-leader oppo. : {supp:.3f}")
    print(f"Suppression effect (should be <= 0): {supp - base:+.3f}")
    print("\n(Small demo sample — scale n_games up for a real estimate.)")
