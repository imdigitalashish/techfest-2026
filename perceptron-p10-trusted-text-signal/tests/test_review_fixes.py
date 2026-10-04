"""Tests for the rubber-duck fixes (research/notes/review-adr001-rubber-duck.md).

Run: cd perceptron-p10-trusted-text-signal && PYTHONPATH=. .venv/bin/python -m pytest -q tests
"""
import numpy as np
import pandas as pd
import pytest

from components.attack.inject import inject_seq, oracle_grid
from components.conformal.methods import aci_from_bounds
from components.trust_scorer.heuristic import score_trust


def _scored(n, rng, texts=None):
    t = pd.Timestamp("2015-03-06")
    return pd.DataFrame({
        "ticker": ["AAA"] * n, "doc_id": [f"d{i}" for i in range(n)],
        "ts_utc": pd.to_datetime(["2015-03-06 15:00"] * n, utc=True),
        "text": texts or [f"$AAA post number {i % 3}" for i in range(n)], "user_id": [f"u{i}" for i in range(n)],
        "user_followers": rng.integers(0, 50_000, n), "user_age_days": rng.uniform(0, 2000, n),
        "user_verified": rng.random(n) < 0.1, "user_statuses": rng.integers(0, 10_000, n),
        "is_retweet": np.zeros(n, bool), "n_cashtags": rng.integers(1, 6, n), "has_url": np.zeros(n, bool),
        "source": ["real"] * n, "trade_date": [t] * n,
        "p_pos": np.full(n, 0.2), "p_neg": np.full(n, 0.2), "p_neu": np.full(n, 0.6), "sentiment": np.zeros(n)})


@pytest.mark.parametrize("seed", range(10))
def test_trust_is_deletion_and_injection_stable(seed):
    rng = np.random.default_rng(seed)
    full = score_trust(_scored(12, rng))
    keep = full.sample(frac=0.5, random_state=seed).drop(columns=["trust", "dup_cluster"])
    sub = score_trust(keep)
    m = full.set_index("doc_id")["trust"].loc[sub["doc_id"]].to_numpy()
    assert np.array_equal(m, sub["trust"].to_numpy())  # removing other docs never changes a doc's trust
    dup = pd.concat([full.drop(columns=["trust", "dup_cluster"]),
                     full.drop(columns=["trust", "dup_cluster"]).assign(doc_id=lambda d: d["doc_id"] + "_copy")])
    both = score_trust(dup).set_index("doc_id")["trust"]
    assert np.array_equal(both.loc[full["doc_id"]].to_numpy(), full["trust"].to_numpy())  # nor does injecting copies


def _aci_run(y, lb, ub, dates, alpha, gamma, rng):
    cal_y = rng.normal(size=200)
    return aci_from_bounds(np.full(200, -1.0), np.full(200, 1.0), cal_y, lb, ub, y, dates, alpha, gamma, stats=(st := {})), st


@pytest.mark.parametrize("seed,gamma", [(0, 0.01), (1, 0.05), (2, 0.005), (3, 0.1)])
def test_aci_long_run_bound_on_adversarial_sequence(seed, gamma):
    rng = np.random.default_rng(seed)
    T, per_day, alpha = 400, 7, 0.1
    dates = np.repeat(np.arange(T), per_day)
    lb, ub = np.full(T * per_day, -1.0), np.full(T * per_day, 1.0)
    scale = np.repeat(np.where((np.arange(T) // 50) % 2 == 0, 0.3, 8.0), per_day)  # abrupt regime switches
    y = rng.standard_t(2, size=T * per_day) * scale
    (lo, hi), st = _aci_run(y, lb, ub, dates, alpha, gamma, rng)
    err = np.array([1 - np.mean((y[dates == d] >= lo[dates == d]) & (y[dates == d] <= hi[dates == d])) for d in range(T)])
    assert abs(err.mean() - st["mean_day_err"]) < 1e-12
    assert abs(err.mean() - alpha) <= (max(alpha, 1 - alpha) + gamma) / (gamma * T) + 1e-12
    assert -gamma - 1e-12 <= st["alpha_min"] and st["alpha_max"] <= 1 + gamma + 1e-12


def test_aci_boundaries_whole_line_and_empty_set():
    rng = np.random.default_rng(0)
    T, alpha, gamma = 120, 0.1, 0.5  # huge step forces alpha_t outside [0, 1]
    dates = np.arange(T)
    y = np.where(np.arange(T) < 60, 0.0, 100.0)  # 60 easy days (alpha_t climbs past 1), then 60 extreme days
    lb, ub = np.full(T, -1.0), np.full(T, 1.0)
    (lo, hi), st = _aci_run(y, lb, ub, dates, alpha, gamma, rng)
    assert st["alpha_le0_days"] > 0 and st["alpha_ge1_days"] > 0
    whole = np.isinf(lo) & np.isinf(hi) & (lo < 0) & (hi > 0)
    empty = lo > hi
    assert whole.any() and empty.any()
    assert np.all((y >= lo) & (y <= hi) | ~whole)  # whole line always covers
    assert not np.any(((y >= lo) & (y <= hi))[empty])  # empty set never covers (no endpoint reordering)


def test_oracle_grid_respects_budget_and_injects():
    for k in (1, 2, 3):
        g = oracle_grid(k)
        assert all(1 <= len(sv) == len(tv) <= k for sv, tv in g)
        assert len(set(g)) == len(g)
    s, w = inject_seq(np.array([0.1]), np.array([0.5]), (1.0, -1.0), (0.05, 0.05))
    assert s.tolist() == [0.1, 1.0, -1.0] and w.tolist() == [0.5, 0.05, 0.05]
