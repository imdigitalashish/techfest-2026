"""Strict simulator (Amendment 1): next-published-quote fills and censoring past the end of the data."""
from __future__ import annotations

import numpy as np
import polars as pl

from components.sim.fills import LegBook
from components.sim.strict import simulate_strict


def _book(ts, bid, ask, sz=1.0):
    ts = np.asarray(ts, dtype=np.int64)
    return LegBook(ts, np.asarray(bid, float), np.asarray(ask, float), np.full(ts.size, sz), np.full(ts.size, sz))


def _intent(t_decide):
    return pl.DataFrame({"opp_id": [0], "t_decide_us": [t_decide], "sell_venue": ["S"], "buy_venue": ["B"],
                         "limit_sell_px": [100.10], "limit_buy_px": [100.02], "size": [0.05], "basis0_bps": [0.0]})


def test_fill_uses_next_published_quote_not_last():
    # S publishes at t=0 (bid 100.10) and t=100 ms (bid 100.00). An order arriving at 50 ms must meet the 100 ms quote.
    books = {"S": _book([0, 100_000, 5_000_000_000], [100.10, 100.00, 100.00], [100.12, 100.02, 100.02]),
             "B": _book([0, 100_000, 5_000_000_000], [100.00, 100.00, 100.00], [100.02, 100.02, 100.02])}
    r = simulate_strict(_intent(0), books, {"S": 50_000.0, "B": 50_000.0}, {"S": 0.0, "B": 0.0})
    assert r["outcome"][0] == "buy_only"          # the sell leg fails: next S quote bids 100.00 < limit 100.10
    assert bool(r["valid"][0])


def test_marks_past_end_of_data_are_censored():
    # Two quotes only; a 10 s markout after arrival has no quote → row must be flagged invalid (not marked at a stale mid).
    books = {"S": _book([0, 1_000], [100.10, 100.10], [100.12, 100.12]), "B": _book([0, 1_000], [100.00, 100.00], [100.02, 100.02])}
    r = simulate_strict(_intent(0), books, {"S": 500.0, "B": 500.0}, {"S": 0.0, "B": 0.0})
    assert r["outcome"][0] == "both"
    assert not bool(r["valid"][0])
