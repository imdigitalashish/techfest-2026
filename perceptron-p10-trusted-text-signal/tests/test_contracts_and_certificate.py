"""Contract + soundness tests. Run: cd perceptron-p10-trusted-text-signal && PYTHONPATH=. .venv/bin/python -m pytest -q tests"""
import itertools

import lightgbm as lgb
import numpy as np
import pandas as pd
import pytest

from architecture.contracts.contracts import DOCS, ContractError, validate
from components.align.calendar import assign_trade_date, leakage_count
from components.robust_conformal.certify import deletion_box, ensemble_bounds, features_from_docs


def _docs(ts_list):
    n = len(ts_list)
    return pd.DataFrame({
        "ticker": ["AAA"] * n, "doc_id": [str(i) for i in range(n)],
        "ts_utc": pd.to_datetime(ts_list, utc=True), "text": ["x"] * n, "user_id": ["u"] * n,
        "user_followers": np.zeros(n, int), "user_age_days": np.ones(n), "user_verified": np.zeros(n, bool),
        "user_statuses": np.zeros(n, int), "is_retweet": np.zeros(n, bool), "n_cashtags": np.ones(n, int),
        "has_url": np.zeros(n, bool), "source": ["real"] * n})


def test_align_cutoff_and_dst():
    days = pd.DatetimeIndex(["2015-03-06", "2015-03-09", "2015-03-10"])  # DST starts Sun 2015-03-08
    d = _docs(["2015-03-06 20:59:00", "2015-03-06 21:00:00",   # EST: 15:59 -> same day, 16:00 -> next day
               "2015-03-09 19:59:00", "2015-03-09 20:00:00"])  # EDT: 15:59 -> same day, 16:00 -> next day
    a = assign_trade_date(d, days)
    assert list(a["trade_date"].dt.strftime("%m-%d")) == ["03-06", "03-09", "03-09", "03-10"]
    assert leakage_count(a) == 0


def test_contract_rejects_bad_source():
    d = _docs(["2015-03-06 15:00:00"])
    d.loc[0, "source"] = "fake"
    with pytest.raises(ContractError):
        validate(d, DOCS)


@pytest.mark.parametrize("seed", range(40))
def test_deletion_box_exact_vs_brute_force(seed):
    rng = np.random.default_rng(seed)
    n, k = int(rng.integers(0, 8)), int(rng.integers(1, 4))
    s = np.round(rng.uniform(-1, 1, n), 2)
    w = rng.uniform(0.05, 1, n)
    lo, hi = deletion_box(s, w, k)
    feats = np.stack([features_from_docs(s[list(keep)], w[list(keep)])
                      for j in range(0, min(k, n) + 1) for keep in itertools.combinations(range(n), n - j)])
    assert np.all(feats >= lo) and np.all(feats <= hi)  # sound, no tolerance
    assert np.allclose(feats.min(0), lo, atol=1e-9) and np.allclose(feats.max(0), hi, atol=1e-9)  # exact up to round-off margin


def test_tree_bounds_are_sound():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(3000, 4))
    y = X[:, 0] - 2 * np.sin(X[:, 1]) + rng.normal(size=3000)
    m = lgb.LGBMRegressor(n_estimators=60, num_leaves=15, verbose=-1, random_state=0).fit(X, y)
    dump = m.booster_.dump_model()
    c = rng.normal(size=(50, 4))
    r = np.abs(rng.normal(size=(50, 4))) * 0.5
    lb, ub = ensemble_bounds(dump, c - r, c + r)
    for _ in range(200):
        p = m.predict(c - r + 2 * r * rng.uniform(size=c.shape))
        assert np.all(p >= lb - 1e-9) and np.all(p <= ub + 1e-9)
    lb0, ub0 = ensemble_bounds(dump, c, c)
    assert np.allclose(lb0, m.predict(c)) and np.allclose(ub0, m.predict(c))
