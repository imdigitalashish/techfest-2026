"""C9 attack — document-injection scenarios for the robustness stretch goal.

* pump(k): k copies of a bullish promotional post from fresh low-follower accounts (weak bot).
  Sentiment = what the deployed text scorer assigns to the template; trust = heuristic trust of such posts.
* oracle(k): worst case within the budget — for every row, try j in 1..k injected documents at
  sentiment +1 or -1 and trust 0.05 or 1; the row counts as covered only if every variant still covers y.
Isolated metric: coverage drop and median-forecast shift caused by the attack.
"""
from __future__ import annotations

import itertools

import numpy as np

from components.robust_conformal.certify import features_from_docs

PUMP_TEMPLATE = "{cashtag} to the moon!!! strong buy, massive breakout, calls printing #bullish"


def inject(s: np.ndarray, w: np.ndarray, j: int, sent: float, trust: float) -> tuple[np.ndarray, np.ndarray]:
    return np.concatenate([s, np.full(j, sent)]), np.concatenate([w, np.full(j, trust)])


def oracle_variants(k: int):
    return [(j, sv, tv) for j, sv, tv in itertools.product(range(1, k + 1), (-1.0, 1.0), (0.05, 1.0))]


def attacked_text_features(docs, variant) -> np.ndarray:
    j, sv, tv = variant
    return np.stack([features_from_docs(*inject(s, w, j, sv, tv)) for s, w in docs])
