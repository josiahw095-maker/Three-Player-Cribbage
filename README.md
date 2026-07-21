# cribbage-sim

A three-handed cribbage engine built to study two questions rigorously:

1. **How much of cribbage is luck vs skill?** (Answer: it's a *curve* in match
   length, not a single percentage — measured, not assumed.)
2. **Is there a single "best move"?** (Two-player: yes, in the equilibrium sense.
   Three-player: no — the kingmaker problem makes optimal play genuinely
   underdetermined. This engine lets you measure the consequences.)

## Design

The whole architecture is one idea: **separate the deterministic rules engine
from pluggable agent policies**, so every experiment is "swap agents, re-run."

```
cribbage/
  cards.py        Card/deck primitives (ranks 1..13, pip values)
  scoring.py      Show-phase scoring — the deterministic, unit-tested core
  pegging.py      Pegging-phase combo scoring (15/31/pairs/runs)
  discard_ev.py   Exact expected-value discard (enumerates all starters), cached
  agents.py       Agent interface + Random, Greedy, NoisyGreedy (tunable skill)
  game.py         Three-handed engine: deal, pegging loop, show, race to 121
  tournament.py   Monte Carlo harness + win-rate edge measurement
tests/
  test_scoring.py Known edge cases incl. the 29 hand and a verified 0 hand
experiments/
  luck_vs_skill.py  Skill edge vs match length (the convergence curve)
  kingmaker.py      Implicit-coalition / leader-suppression effect
```

Scoring is the bedrock: it's pure arithmetic with no hidden information, so it
can be exhaustively tested. Everything else assumes it's correct.

## Quick start

```bash
python tests/test_scoring.py         # verify the core
python experiments/luck_vs_skill.py  # skill edge vs match length
python experiments/kingmaker.py      # trailing-player influence
```

```python
import random
from cribbage.agents import GreedyAgent, RandomAgent
from cribbage.tournament import run_tournament

wins = run_tournament([GreedyAgent(), RandomAgent(), RandomAgent()], n_games=1500)
print(wins)  # greedy (seat 0) wins ~90% — the engine rewards skill
```

## Rules implemented

Common three-hand variant: 5 cards dealt each, one card off the top seeds the
crib, each player discards 1 (crib = 4). Dealer owns the crib; deal rotates.
Pegging, then show (eldest hand first, dealer last, then crib). First to 121
wins immediately.

## Status / roadmap

Working: rules engine, scoring (tested), three-handed game loop, exact-EV
discard, baseline agents, Monte Carlo harness, two experiment skeletons.

Deliberate simplifications and good next steps (roughly increasing difficulty):

- **Discard**: add expected *crib* value (positive when dealer, negative when
  feeding an opponent) and reweight by P(reach 121 first) near the end.
- **Pegging**: replace the myopic heuristic with search / CFR. The two-player
  state-of-the-art is Monte Carlo Counterfactual Regret Minimization; the
  three-player extension is open and is the most interesting part of the project.
- **Performance**: the pegging/game inner loop is pure Python. Profile it; the
  hot path is a good candidate for `numba`, Cython, or a Rust core if you scale
  experiments to millions of games.
- **Kingmaker**: the current AntiLeaderAgent is intentionally naive (and its
  crude "dump high card" tactic actually *helps* the leader — a real finding).
  Sharpen the leader definition and the suppression policy, and measure whether
  a *good* trailing-player policy can suppress a leader without self-harm.
- **Luck/skill**: scale the sample sizes up and plot the full convergence curve
  (skill's share of outcome variance vs number of games) as the headline result.

## Notes

Sample sizes in the experiment scripts are tiny so they finish in seconds. Scale
`n_games`/`n_matches` up for real estimates — the numbers printed by default are
illustrative of the *method*, not converged.
