"""Exhaustive-ish tests for the scoring core. Run: python -m pytest -q
(or just `python tests/test_scoring.py` for a plain-assert run).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cribbage.cards import Card
from cribbage.scoring import score_hand


def test_perfect_29():
    # 5-5-5-J in hand, J matches the starter suit; starter is the 4th five.
    hand = [Card(5, "C"), Card(5, "D"), Card(5, "H"), Card(11, "S")]
    starter = Card(5, "S")
    assert score_hand(hand, starter) == 29


def test_zero_hand():
    hand = [Card(1, "S"), Card(2, "S"), Card(6, "S"), Card(10, "H")]
    starter = Card(11, "H")
    assert score_hand(hand, starter) == 0


def test_double_run_and_fifteen():
    # 4-5-5-6 + 4 starter: double-double run territory.
    hand = [Card(4, "S"), Card(5, "H"), Card(5, "D"), Card(6, "C")]
    starter = Card(4, "H")
    # runs: two runs 4-5-6 twice over doubled 4 and 5 -> 4*3=... check via engine
    # pairs: two 4s (2) + two 5s (2) = 4 ; fifteens: 4+5+6=15 x (2*2*1)=... 
    # We assert the engine's value is internally consistent and > 0.
    assert score_hand(hand, starter) == 24


def test_flush_hand_vs_crib():
    hand = [Card(2, "H"), Card(4, "H"), Card(6, "H"), Card(8, "H")]
    starter = Card(10, "S")  # not a heart
    # four-card flush counts in hand (4) but not in crib (0). fifteens: 6+... 
    assert score_hand(hand, starter, is_crib=False) - score_hand(hand, starter, is_crib=True) == 4


def test_nobs():
    # Chosen so the ONLY score is nobs: no fifteen, pair, run, or flush.
    hand = [Card(11, "D"), Card(13, "S"), Card(8, "C"), Card(4, "H")]
    starter = Card(2, "D")  # matches the Jack's suit -> 1 for nobs
    assert score_hand(hand, starter) == 1


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("all scoring tests passed")
