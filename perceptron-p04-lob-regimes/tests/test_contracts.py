"""Contract and leakage tests (run: cd perceptron-p04-lob-regimes && python -m pytest -q tests).

Synthetic books only, so the tests need no downloaded data.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from components.adapter import Context, run_episode  # noqa: E402
from components.contracts import BookDay  # noqa: E402
from components.evaluator import block_bootstrap_ci, score  # noqa: E402
from components.features import build_features  # noqa: E402
from components.forecaster import LogisticHead  # noqa: E402
from components.labeler import make_labels  # noqa: E402
from components.normalizer import EWMANorm, StaticNorm  # noqa: E402
from components.shift_detector import PageHinkley, RollingKS  # noqa: E402

DAY0 = 1_700_006_400 * 1_000_000  # 2023-11-15 00:00:00 UTC in microseconds


def synth_book(n: int = 40_000, seed: int = 0, hours: float = 1.0) -> BookDay:
    rng = np.random.default_rng(seed)
    recv = np.sort(DAY0 + rng.integers(0, int(hours * 3600e6), n)).astype(np.int64)
    mid_ticks = 300_000 + np.cumsum(rng.integers(-1, 2, n))
    bid0 = mid_ticks * 0.1
    lv = np.arange(5) * 0.1
    bid_px = bid0[:, None] - lv[None, :]
    ask_px = (bid0 + 0.1)[:, None] + lv[None, :]
    return BookDay("BTCUSDT", "2023-11-15", recv, recv - 3000, bid_px, rng.exponential(1, (n, 5)),
                   ask_px, rng.exponential(1, (n, 5)))


def _cut(book: BookDay, upto_us: int, perturb: bool) -> BookDay:
    """Same past, different (or absent) future after upto_us."""
    m = book.recv_us <= upto_us
    if not perturb:
        sl = lambda a: a[m]
        return BookDay(book.symbol, book.day, sl(book.recv_us), sl(book.exch_us), sl(book.bid_px),
                       sl(book.bid_sz), sl(book.ask_px), sl(book.ask_sz))
    rng = np.random.default_rng(99)
    bs, as_ = book.bid_sz.copy(), book.ask_sz.copy()
    bs[~m] = rng.exponential(5, bs[~m].shape)
    as_[~m] = rng.exponential(5, as_[~m].shape)
    bp, ap = book.bid_px.copy(), book.ask_px.copy()
    bp[~m] += 1.0
    ap[~m] += 1.0
    return BookDay(book.symbol, book.day, book.recv_us, book.exch_us, bp, bs, ap, as_)


def test_features_are_causal():
    book = synth_book()
    cut_us = DAY0 + 1800 * 1_000_000
    f_full = build_features(book, drop_warmup=False)
    f_pert = build_features(_cut(book, cut_us, perturb=True), drop_warmup=False)
    past = f_full.grid_us <= cut_us
    assert past.sum() > 1000
    np.testing.assert_allclose(f_full.X[past], f_pert.X[past], rtol=0, atol=1e-9)
    np.testing.assert_allclose(f_full.mid[past], f_pert.mid[past])


def test_labels_use_future_only_and_report_availability():
    f = build_features(synth_book(), drop_warmup=False)
    L = make_labels(f, 10)
    t = 500
    if not np.isnan(L.y[t]):
        assert L.y[t] == float(f.mid[t + 10] > f.mid[t])
    assert L.avail_step[t] == t + 10
    assert np.all(np.isnan(L.y[-10:]))


def test_ewma_norm_is_causal():
    rng = np.random.default_rng(1)
    X = rng.normal(size=(1000, 3))
    n = EWMANorm(np.zeros(3), np.ones(3), 100)
    Z1 = n.transform(X)
    X2 = X.copy()
    X2[600:] *= 50
    Z2 = n.transform(X2)
    np.testing.assert_allclose(Z1[:600], Z2[:600])


def test_adapter_never_reads_labels_before_available():
    """If labels after step s are corrupted, predictions up to s + h must not change."""
    rng = np.random.default_rng(2)
    T, d, H = 3000, 4, 10
    from components.contracts import FeatureFrame, Labels
    X = rng.normal(size=(T, d))
    grid = DAY0 + np.arange(T, dtype=np.int64) * 1_000_000
    names = ("a", "b", "rv_600s_bps", "c")
    X[:, 2] = np.abs(X[:, 2])
    f = FeatureFrame("BTCUSDT", "x", 1_000_000, grid, names, X, np.full(T, 100.0), np.ones(T))
    y = (rng.random(T) < 1 / (1 + np.exp(-X[:, 0]))).astype(float)
    L1 = Labels(H, y, np.arange(T) + H, np.zeros(T))
    y2 = y.copy()
    s = 1500
    y2[s:] = 1 - y2[s:]
    L2 = Labels(H, y2, np.arange(T) + H, np.zeros(T))
    sn = StaticNorm.fit(X)
    head = LogisticHead(d).fit(sn.transform(X), y)
    cfg = {"fs_eta": 1.0, "fs_alpha": 1e-3, "fs_alpha_boost": 0.05, "fs_boost_steps": 50, "sgd_l2": 1e-3,
           "refit_lam": 10.0, "ks_features": ["a"], "ks": {"window": 200, "subsample": 5, "stride": 10},
           "ph": {"delta": 0.005, "threshold": 5.0, "min_n": 50}}
    ctx = Context(names, sn, EWMANorm(sn.mu, sn.sd ** 2, 300), {"static": head, "ewma": head},
                  {"static": [head] * 3, "ewma": [head] * 3}, np.array([0.5, 1.0]), X[::5, :1], [0], cfg)
    spec = {"norm": "ewma", "heads": [("static",), ("sgd", 0.01), ("periodic", 300, 600), ("alarm_refit", 300, 100)],
            "combine": "fixed_share", "detectors": ["ph"], "on_alarm": ["refit", "boost"]}
    p1 = run_episode("t", f, L1, ctx, spec).p_up
    p2 = run_episode("t", f, L2, ctx, spec).p_up
    np.testing.assert_allclose(p1[: s + H + 1], p2[: s + H + 1])
    assert not np.allclose(p1[s + H + 1:], p2[s + H + 1:])
    # v2 spike paths: coin expert + harm gate (+ boost) must respect label availability too
    ctx.cfg["harm"] = {"k": 0.0, "threshold": 2.0, "min_n": 20, "cooldown": 100}
    spec2 = {"norm": "ewma", "heads": [("static",), ("sgd", 0.01), ("regime", 0), ("coin",)],
             "combine": "fixed_share", "detectors": ["harm"], "on_alarm": ["boost"]}
    q1 = run_episode("t2", f, L1, ctx, spec2).p_up
    q2 = run_episode("t2", f, L2, ctx, spec2).p_up
    np.testing.assert_allclose(q1[: s + H + 1], q2[: s + H + 1])
    assert not np.allclose(q1[s + H + 1:], q2[s + H + 1:])


def test_detectors_fire_on_obvious_shift_and_not_on_iid():
    rng = np.random.default_rng(3)
    ref = rng.normal(size=(2000, 1))
    X = np.concatenate([rng.normal(size=(3000, 1)), rng.normal(3, 1, size=(3000, 1))])
    ks = RollingKS(ref, [0], ["a"], window=300, subsample=5, stride=10, alpha=1e-3, persist=2, cooldown=10**9)
    alarms = [a for t in range(len(X)) if (a := ks.update(t, X))]
    assert len(alarms) == 1 and 3000 <= alarms[0].step <= 3400
    ph = PageHinkley(delta=0.01, threshold=10.0, min_n=100)
    calm = [ph.update(t, x) for t, x in enumerate(rng.normal(0.69, 0.05, 3000))]
    assert not any(calm)
    hits = [a for t, x in enumerate(rng.normal(0.80, 0.05, 2000)) if (a := ph.update(t, x))]
    assert hits


def test_metrics():
    y = np.array([0, 1, 1, 0, np.nan] * 40, dtype=float)
    p = np.where(y == 1, 0.8, 0.2)
    s = score(p, y)
    assert s["acc"] == 1.0 and s["auc"] == 1.0 and abs(s["logloss"] + np.log(0.8)) < 1e-9
    m, lo, hi = block_bootstrap_ci(np.ones(5000), block=100)
    assert m == 1.0 and lo == 1.0 and hi == 1.0


def test_fast_ks_matches_scipy_exactly():
    from scipy.stats import ks_2samp
    from components.shift_detector import ks_pvalue_asymp, ks_stat_sorted
    rng = np.random.default_rng(7)
    for trial in range(200):
        n, m = int(rng.integers(50, 5000)), int(rng.integers(5, 80))
        a = rng.normal(size=n)
        b = rng.normal(rng.normal(0, 0.5), 1, size=m)
        if trial % 3 == 0:  # heavy ties, like spread_ticks
            a, b = np.round(a), np.round(b)
        r = ks_2samp(b, a, method="asymp")
        d = ks_stat_sorted(b, np.sort(a))
        assert abs(d - r.statistic) < 1e-12
        assert abs(ks_pvalue_asymp(d, m, n) - r.pvalue) < 1e-12


def test_harm_cusum_fires_only_when_worse_than_coin_flip():
    from components.shift_detector import LN2, HarmCUSUM
    rng = np.random.default_rng(8)
    # Threshold in nats; ARL0 grows ~exp(2*|drift|*H/var), so H=15 is quiet for a model 0.04 nats
    # better than a coin flip (sd 0.3) while a 0.05-nat harmful excess is caught in ~300 labels.
    h = HarmCUSUM(k=0.0, threshold=15.0, min_n=60, cooldown=600)
    good = [h.update(t, x) for t, x in enumerate(rng.normal(LN2 - 0.04, 0.3, 20000))]
    assert sum(a is not None for a in good) <= 1
    bad = [a for t, x in enumerate(rng.normal(LN2 + 0.05, 0.3, 3000), start=20000) if (a := h.update(t, x))]
    assert bad and bad[0].step < 20000 + 1000
