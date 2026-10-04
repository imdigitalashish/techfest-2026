"""C11 DP Publisher — Laplace mechanism for count tables, a validated and persistent privacy-budget ledger, and
small-cell suppression.

Noise comes from fresh OS entropy (`secrets`) unless a seed is injected; seeds are for SIMULATION/TESTS ONLY — a
production release must never use or publish a seed, or anyone with the code could replay the noise and recover the
exact counts (code-review issue 2). One ledger must cover every table released over the same population and period
(unit, district, gender splits, months): budgets compose (issue 9).
"""
from __future__ import annotations

import json
import math
import os
import secrets
import tempfile

import numpy as np
import pandas as pd


def _valid_eps(x) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(x) and x > 0


class Ledger:
    def __init__(self, total_epsilon: float, path: str | None = None):
        if not _valid_eps(total_epsilon):
            raise ValueError("total epsilon must be finite and > 0")
        self.total, self.path, self.spent, self.entries = float(total_epsilon), path, 0.0, []
        if path and os.path.exists(path):
            st = json.load(open(path))
            if st["total"] != self.total:
                raise ValueError("ledger total differs from the persisted ledger")
            self.spent, self.entries = float(st["spent"]), [tuple(e) for e in st["entries"]]

    def charge(self, eps: float, table: str):
        if not _valid_eps(eps):
            raise ValueError("epsilon must be finite and > 0")
        if self.spent + eps > self.total + 1e-12:
            raise PermissionError(f"privacy budget exhausted: spent {self.spent}, asked {eps}, total {self.total}")
        self.spent += eps
        self.entries.append((table, eps))
        if self.path:
            fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(self.path)))
            with os.fdopen(fd, "w") as f:
                json.dump({"total": self.total, "spent": self.spent, "entries": self.entries}, f)
            os.replace(tmp, self.path)  # atomic


def release_rates(counts: pd.DataFrame, eps: float, ledger: Ledger, table: str, min_cell: int = 20,
                  seed: int | None = None) -> pd.DataFrame:
    """counts: index unit, columns numerator, denominator (each person in exactly one row of this table).
    eps is split equally between numerator and denominator (sensitivity 1 each); noisy denominators < min_cell are
    suppressed. seed=None (production) draws secret noise."""
    ledger.charge(eps, table)
    rng = np.random.default_rng(secrets.randbits(128) if seed is None else seed)
    num = counts["numerator"] + rng.laplace(0, 2.0 / eps, len(counts))
    den = counts["denominator"] + rng.laplace(0, 2.0 / eps, len(counts))
    out = pd.DataFrame({"rate": (num / den).clip(0, 1), "noisy_denominator": den.round()}, index=counts.index)
    out.loc[out["noisy_denominator"] < min_cell, "rate"] = np.nan
    return out
