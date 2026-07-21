"""Three-handed cribbage game engine.

Rules implemented (a common three-hand variant):
  - 3 players, 5 cards each; one card dealt off the top to seed the crib.
  - Each player discards exactly 1 to the crib (crib = 4 cards).
  - Dealer owns the crib. Deal rotates each hand.
  - Pegging then show; eldest hand (left of dealer) counts first, dealer last,
    then the crib. First to 121 wins immediately.

Simplifications flagged in comments are deliberate starting points to extend.
"""

from __future__ import annotations
import random

from .cards import Card, make_deck
from .scoring import score_hand
from .pegging import peg_points

WIN = 121


class GameState:
    def __init__(self, n=3):
        self.scores = [0] * n
        self.winner: int | None = None

    def add(self, player: int, pts: int) -> bool:
        """Add points; return True if this player just won (race stops)."""
        if self.winner is not None or pts <= 0:
            return self.winner == player
        self.scores[player] += pts
        if self.scores[player] >= WIN:
            self.scores[player] = WIN
            self.winner = player
            return True
        return False


def _pegging(hands, dealer, state, agents):
    """Run the pegging phase for 3 players. hands: list of lists (4 cards each).
    Play starts to the dealer's left. Returns without finishing if someone wins.
    """
    n = len(hands)
    remaining = [list(h) for h in hands]
    turn = (dealer + 1) % n

    pile: list[Card] = []
    count = 0
    passed = [False] * n  # said "go" at the current count
    last_player = None

    def cards_left():
        return sum(len(r) for r in remaining)

    while cards_left() > 0:
        legal = [c for c in remaining[turn] if count + c.value <= 31]
        if legal and not passed[turn]:
            card = agents[turn].play(legal, pile, count, state)
            remaining[turn].remove(card)
            pile.append(card)
            count += card.value
            last_player = turn
            if state.add(turn, peg_points(pile, count)):
                return
            if count == 31:
                # reset sub-round; the player who hit 31 already scored for it.
                pile, count = [], 0
                passed = [False] * n
        else:
            passed[turn] = True
            # Has everyone who still holds cards passed? -> award the go.
            active = [p for p in range(n) if remaining[p]]
            if all(passed[p] for p in active):
                if last_player is not None and count != 31:
                    if state.add(last_player, 1):  # go point
                        return
                pile, count = [], 0
                passed = [False] * n
                # New sub-round starts left of whoever played last.
                if last_player is not None:
                    turn = (last_player + 1) % n
                    continue
        turn = (turn + 1) % n

    # Last card of the whole phase: 1 for last (if it wasn't a 31, already scored)
    if last_player is not None and count != 31:
        state.add(last_player, 1)


def play_hand(agents, dealer, rng: random.Random, state: GameState):
    """Play one full hand (deal, discard, peg, show). Mutates `state`."""
    n = len(agents)
    deck = make_deck()
    rng.shuffle(deck)

    hands = [ [deck.pop() for _ in range(5)] for _ in range(n) ]
    crib = [deck.pop()]  # seed the crib with one card off the top

    kept = []
    for p in range(n):
        keep, disc = agents[p].discard(hands[p], is_dealer=(p == dealer))
        kept.append(keep)
        crib.append(disc)

    starter = deck.pop()
    # His heels: dealer scores 2 if the starter is a Jack.
    if starter.rank == 11:
        if state.add(dealer, 2):
            return

    _pegging(kept, dealer, state, agents)
    if state.winner is not None:
        return

    # Show: eldest hand first, around to dealer, then crib.
    order = [(dealer + 1 + i) % n for i in range(n)]
    for p in order:
        if state.add(p, score_hand(kept[p], starter)):
            return
    state.add(dealer, score_hand(crib, starter, is_crib=True))


def play_game(agents, rng: random.Random | None = None, start_dealer: int = 0) -> int:
    """Play a full game to 121. Returns the index of the winning agent."""
    rng = rng or random.Random()
    state = GameState(len(agents))
    dealer = start_dealer
    while state.winner is None:
        play_hand(agents, dealer, rng, state)
        dealer = (dealer + 1) % len(agents)
    return state.winner
