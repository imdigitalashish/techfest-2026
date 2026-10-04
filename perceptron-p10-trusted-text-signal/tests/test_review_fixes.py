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


# ---- cross-model review fixes (reviews/2026-10-04-*.md) ----
from components.attack.inject import inject  # noqa: E402
from components.robust_conformal.certify import deletion_box, features_from_docs  # noqa: E402
from eval.metrics import evaluate  # noqa: E402


@pytest.mark.parametrize("k", [1, 3])
def test_high_count_constant_sentiment_is_inside_box(k):
    """gpt-6-sol B2: 49,997 identical clean posts + k identical injected posts (value emitted by MiniLM)."""
    v = 0.9204812125498814
    s, w = np.full(49_997, v), np.full(49_997, 0.05)
    s2, w2 = inject(s, w, k, v, 0.05)
    lo, hi = deletion_box(s2, w2, k)
    f = features_from_docs(s, w)
    assert np.all(f >= lo) and np.all(f <= hi)


@pytest.mark.parametrize("seed", range(5))
def test_high_count_random_injection_is_inside_box(seed):
    rng = np.random.default_rng(seed)
    n = int(rng.integers(5_000, 60_000))
    s = np.clip(rng.normal(rng.uniform(-0.9, 0.9), rng.choice([1e-9, 1e-4, 0.3]), n), -1, 1)
    w = rng.uniform(0.05, 1, n)
    s2, w2 = inject(s, w, 3, float(rng.choice([-1.0, 1.0])), 1.0)
    lo, hi = deletion_box(s2, w2, 3)
    f = features_from_docs(s, w)
    assert np.all(f >= lo) and np.all(f <= hi)


def test_box_rejects_more_than_max_docs():
    with pytest.raises(ValueError):
        deletion_box(np.zeros(1_000_001), np.zeros(1_000_001), 1)


def test_empty_interval_is_a_miss_and_never_scored_as_a_point():
    """gpt-6-sol N1."""
    d = pd.Timestamp("2015-07-01")
    iv = pd.DataFrame({"ticker": ["A", "B"], "trade_date": [d, d], "lo": [1.0, -1.0], "hi": [0.0, 1.0],
                       "point": [0.0, 0.0], "method": ["x", "x"]})
    truth = pd.DataFrame({"ticker": ["A", "B"], "trade_date": [d, d], "y": [1.0, 0.0]})
    e = evaluate(iv, truth, 0.1)
    assert e["coverage"] == 0.5 and e["frac_empty"] == 0.5
    assert e["mean_width"] == 2.0 and e["winkler"] == 2.0  # empty row excluded from width/Winkler, reported via frac_empty


def test_pump_scoring_dispatch_rejects_unsupported_scorers():
    """gpt-6-sol N2: the FinBERT option must not silently fall back to VADER."""
    from eval.run_baselines import template_sentiment
    assert -1.0 <= template_sentiment("vader") <= 1.0
    with pytest.raises(NotImplementedError):
        template_sentiment("finbert")


def test_separately_adapted_aci_runs_are_not_nested():
    """gpt-6-sol B1 / gpt-6-astra #1 (documented limitation): same raw bounds on day 2, but the attacked run's
    alpha_t moved differently on day 1, so its day-2 interval can miss where the clean run covers. Per-row
    containment is claimed only at a shared offset (fixed-offset certified CQR)."""
    cal = np.linspace(0.01, 1.0, 100)
    kw = dict(cal_lb=np.zeros(100), cal_ub=np.zeros(100), y_cal=cal, alpha=0.1, gamma=0.01)
    y, dates = np.array([1.05, 0.92]), np.array([0, 1])
    lo_c, hi_c = aci_from_bounds(lb=np.zeros(2), ub=np.zeros(2), y=y, dates=dates, **kw)
    lo_a, hi_a = aci_from_bounds(lb=np.array([-2.0, 0.0]), ub=np.array([2.0, 0.0]), y=y, dates=dates, **kw)
    assert lo_c[1] <= y[1] <= hi_c[1]
    assert not (lo_a[1] <= y[1] <= hi_a[1])
