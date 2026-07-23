"""Agent policies. Swap these to run different strategies against each other.

An Agent implements two decisions:
  - discard(hand, is_dealer): return (kept_4, discarded_1)
  - play(legal, pile, count, state): choose one card to play during pegging

Keeping the rules engine and the policies separate is the whole point of the
architecture: every experiment is "plug in different agents and re-run".
"""

from __future__ import annotations
import random

from .cards import Card
from .discard_ev import best_discard
from .pegging import peg_points


class Agent:
    name = "base"

    def discard(self, hand: list[Card], is_dealer: bool) -> tuple[list[Card], Card]:
        raise NotImplementedError

    def play(self, legal: list[Card], pile: list[Card], count: int, state=None) -> Card:
        raise NotImplementedError


class RandomAgent(Agent):
    name = "random"

    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()

    def discard(self, hand, is_dealer):
        kept = self.rng.sample(hand, 4)
        discarded = next(c for c in hand if c not in kept)
        return kept, discarded

    def play(self, legal, pile, count, state=None):
        return self.rng.choice(legal)


class NoisyGreedyAgent(Agent):
    """Greedy, but with probability `epsilon` makes a random decision instead.

    This is the skill knob for luck-vs-skill experiments: epsilon=0 is the full
    greedy strategy, epsilon=1 is fully random. Pairing two agents with a small
    epsilon gap lets you measure how a *tiny* skill difference converts to win
    rate as a function of match length.
    """

    def __init__(self, epsilon: float = 0.1, rng: random.Random | None = None):
        self.epsilon = epsilon
        self.rng = rng or random.Random()
        self.name = f"greedy(eps={epsilon})"
        self._greedy = GreedyAgent(self.rng)
        self._random = RandomAgent(self.rng)

    def discard(self, hand, is_dealer):
        a = self._random if self.rng.random() < self.epsilon else self._greedy
        return a.discard(hand, is_dealer)

    def play(self, legal, pile, count, state=None):
        a = self._random if self.rng.random() < self.epsilon else self._greedy
        return a.play(legal, pile, count, state)


class GreedyAgent(Agent):
    """Exact-EV discard; myopic pegging (grab the most immediate points, else
    prefer playing low to keep options / avoid handing 15s and 31s)."""

    name = "greedy"

    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()

    def discard(self, hand, is_dealer):
        # NOTE: ignores crib ownership. A real improvement is to add expected
        # crib value (positive if is_dealer, negative otherwise).
        return best_discard(hand)

    def play(self, legal, pile, count, state=None):
        best, best_pts = None, -1
        for c in legal:
            pts = peg_points(pile + [c], count + c.value)
            # Tie-break: take the points, otherwise play the higher card so the
            # small cards stay available near the 31 boundary.
            key = (pts, -c.value) if pts > 0 else (0, c.value)
            score = key[0] * 100 + key[1]
            if score > best_pts:
                best, best_pts = c, score
        return best


class HighestOrFifteenAgent(Agent):
    """Myopic pegging: play the card that hits 15 if one is available,
    otherwise play the highest-value legal card."""

    name = "highest_or_15"

    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()

    def discard(self, hand, is_dealer):
        return best_discard(hand)

    def play(self, legal, pile, count, state=None):
        for c in legal:
            if count + c.value == 15:
                return c
        return max(legal, key=lambda c: c.value)
