"""Contract + behaviour tests for the walking skeleton (synthetic, deterministic data)."""
from __future__ import annotations

import numpy as np
import polars as pl
import pytest

from architecture.contracts.frames import OPPORTUNITY_FRAME, QUOTE_FRAME, check
from architecture.contracts.models import Quote
from components.decay.survival import add_features, fit_km
from components.decision import policies as P
from components.detector.cross import detect, opportunity_contract_view
from components.sim.fills import simulate, truth_books


def _quotes(rows):
    df = pl.DataFrame(rows, schema=["ts_exch_us", "venue", "instrument", "bid_px", "ask_px"], orient="row")
    return df.with_columns(
        pl.col("ts_exch_us").alias("ts_recv_us"), pl.lit(False).alias("exch_ts_imputed"),
        pl.lit(1.0).alias("bid_sz"), pl.lit(1.0).alias("ask_sz"),
    ).select(list(QUOTE_FRAME)).cast(QUOTE_FRAME).with_columns((pl.col("venue") + ":" + pl.col("instrument")).alias("leg"))


def _scenario():
    s = 1_000_000  # 1 s in µs
    rows = []
    for k in range(200):  # 200 s of aligned, uncrossed quotes to warm up the fair basis (~0)
        rows += [(k * s, "A", "X", 100.00, 100.02), (k * s + 10, "B", "X", 100.00, 100.02)]
    t0 = 200 * s
    rows += [(t0, "A", "X", 100.10, 100.12),          # A jumps: bid_A − ask_B = 8 bps → cross opens
             (t0 + 5_000, "B", "X", 100.10, 100.12)]  # B catches up 5 ms later → cross closes
    rows += [(t0 + 10 * s, "A", "X", 100.10, 100.12), (t0 + 10 * s + 10, "B", "X", 100.10, 100.12)]
    return _quotes(rows)


def test_quote_contract_rejects_crossed_book():
    with pytest.raises(ValueError):
        Quote(ts_exch_us=1, ts_recv_us=1, venue="v", instrument="i", bid_px=10, bid_sz=1, ask_px=9, ask_sz=1)


def test_detector_finds_one_episode_with_exact_duration():
    q = _scenario()
    check(q.drop("leg"), QUOTE_FRAME)
    opp = detect(q, ["A:X", "B:X"], "ts_exch_us", theta_bps=1.0, warmup_s=100)
    check(opportunity_contract_view(opp), OPPORTUNITY_FRAME)
    assert opp.height == 1
    r = opp.row(0, named=True)
    assert r["sell_venue"] == "A:X" and r["buy_venue"] == "B:X"
    assert r["duration_us"] == 5_000 and not r["censored"]
    assert 7.0 < r["edge0_bps"] < 9.0


def test_sim_fills_only_while_cross_alive():
    q = _scenario()
    opp = add_features(detect(q, ["A:X", "B:X"], "ts_exch_us", theta_bps=1.0, warmup_s=100))
    opp = P.with_net(opp, "f0").with_columns(pl.col("t_start_us").alias("t_obs_us"), pl.col("duration_us").alias("duration_obs_us"))
    books = truth_books(q)
    fees = {"A:X": 0.0, "B:X": 0.0}
    fast = simulate(P.naive(opp, 0.0), books, {"A:X": 1_000.0, "B:X": 1_000.0}, fees)    # 1 ms: before B moves
    slow = simulate(P.naive(opp, 0.0), books, {"A:X": 20_000.0, "B:X": 20_000.0}, fees)  # 20 ms: after B moved
    assert fast["outcome"][0] == "both" and fast["pnl_usd"][0] > 0
    assert slow["outcome"][0] == "sell_only"   # B's ask moved above our limit; A still bids 100.10


def test_survival_is_monotone():
    q = _scenario()
    opp = add_features(detect(q, ["A:X", "B:X"], "ts_exch_us", theta_bps=1.0, warmup_s=100))
    km = fit_km(pl.concat([opp] * 30))
    s = km.survival(np.array([0.1, 1, 4, 6, 100]))[0]
    assert np.all(np.diff(s) <= 1e-12) and s[0] == 1.0 and s[-1] == 0.0
