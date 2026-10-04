"""C5 Calibrate & decode v0: TRLDistribution -> TRLDecision.

No calibration is fitted yet: `confidence` is the model's (uncalibrated) probability of the decoded level.
Supported rules: mode, median, expectation. Unknown rules raise (no silent fallback); QWK-tuned thresholds are TODO.
"""
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
    elif rule == "median":
        trl = int(LEVELS[(cdf >= 0.5).argmax()])
    else:
        raise ValueError(f"unknown or unimplemented decode rule {rule!r}; supported: mode, median, expectation")
    lo, hi = int(LEVELS[(cdf >= 0.1).argmax()]), int(LEVELS[(cdf >= 0.9).argmax()])
    return {"trl": trl, "decode_rule": rule, "confidence": float(p[trl - 1]),
            "interval80": [lo, max(lo, hi)], "abstain": bool(n_chars < 200)}
