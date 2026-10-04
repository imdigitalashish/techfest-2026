"""C11 DP Publisher — Laplace mechanism for count tables with a privacy-budget ledger and small-cell suppression."""
from __future__ import annotations

import numpy as np
import pandas as pd


class Ledger:
    def __init__(self, total_epsilon: float):
        self.total, self.spent, self.entries = total_epsilon, 0.0, []

    def charge(self, eps: float, table: str):
        if self.spent + eps > self.total + 1e-12:
            raise PermissionError(f"privacy budget exhausted: spent {self.spent}, asked {eps}, total {self.total}")
        self.spent += eps
        self.entries.append((table, eps))


def release_rates(counts: pd.DataFrame, eps: float, ledger: Ledger, table: str, min_cell: int = 20, seed: int = 0) -> pd.DataFrame:
    """counts: index unit, columns numerator, denominator (person counts; each person in one unit).
    Splits eps equally between numerator and denominator (sensitivity 1 each); suppresses noisy denominators < min_cell."""
    ledger.charge(eps, table)
    rng = np.random.default_rng(seed)
    num = counts["numerator"] + rng.laplace(0, 2.0 / eps, len(counts))
    den = counts["denominator"] + rng.laplace(0, 2.0 / eps, len(counts))
    rate = (num / den).clip(0, 1)
    out = pd.DataFrame({"rate": rate, "noisy_denominator": den.round()}, index=counts.index)
    out.loc[out["noisy_denominator"] < min_cell, "rate"] = np.nan
    return out
