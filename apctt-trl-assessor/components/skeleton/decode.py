"""C5 Calibrate & decode v0: TRLDistribution -> TRLDecision (no calibration fitted yet; rule is configurable)."""
from __future__ import annotations

import numpy as np

LEVELS = np.arange(1, 10)


def decide(dist: dict, rule: str = "median", n_chars: int = 1) -> dict:
    p = np.asarray(dist["p"], dtype=float)
    cdf = np.cumsum(p)
    if rule == "mode":
        trl = int(LEVELS[p.argmax()])
    elif rule == "expectation":
        trl = int(np.clip(np.rint(p @ LEVELS), 1, 9))
    else:
        rule, trl = "median", int(LEVELS[(cdf >= 0.5).argmax()])
    lo, hi = int(LEVELS[(cdf >= 0.1).argmax()]), int(LEVELS[(cdf >= 0.9).argmax()])
    return {"trl": trl, "decode_rule": rule, "confidence": float(p[trl - 1]),
            "interval80": [lo, max(lo, hi)], "abstain": bool(n_chars < 200)}
