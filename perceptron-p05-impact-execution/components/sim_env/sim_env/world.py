"""Build and run one ABIDES rmsc04 world with exactly one extra agent appended.

Counterfactual twins: the treatment arm appends our execution agent; the twin arm
appends an ExecutionAgent with quantity 0, which never sends an order. Both arms
append exactly one agent, so the latency model that ``config_add_agents``
re-draws from the global RNG is identical, and every background agent keeps its
own seeded RandomState. Divergence between the arms is caused by our orders alone.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Callable, Dict, List

import numpy as np

from . import ABIDES_DIR  # noqa: F401  (path setup side effect)

warnings.filterwarnings("ignore")

from abides_core import abides  # noqa: E402
from abides_core.utils import str_to_ns  # noqa: E402
from abides_markets.configs import rmsc04  # noqa: E402
from abides_markets.utils import config_add_agents  # noqa: E402

TICKER = "ABM"
DATE = "20210205"


def ns_at(hhmmss: str, date: str = DATE) -> int:
    import pandas as pd

    return int(pd.to_datetime(date).value) + str_to_ns(hhmmss)


@dataclass
class WorldResult:
    seed: int
    t: np.ndarray            # book-update times (ns)
    bid: np.ndarray          # best bid (cents), NaN if empty
    ask: np.ndarray          # best ask (cents), NaN if empty
    bid_q: np.ndarray        # touch depth, bid side
    ask_q: np.ndarray        # touch depth, ask side
    holdings_by_type: Dict[str, int]
    agent_record: Dict = field(default_factory=dict)
    volume: float = 0.0
    tx_t: np.ndarray = None  # executed-trade times (ns), aggressor side recorded once
    tx_q: np.ndarray = None  # executed-trade quantities

    def mid_at(self, times_ns: np.ndarray, strictly_before: bool = False) -> np.ndarray:
        """Mid price at each query time (last two-sided book state at or before it)."""
        mid = (self.bid + self.ask) / 2.0
        ok = ~np.isnan(mid)
        tt, mm = self.t[ok], mid[ok]
        side = "left" if strictly_before else "right"
        idx = np.searchsorted(tt, times_ns, side=side) - 1
        out = np.where(idx >= 0, mm[np.clip(idx, 0, len(mm) - 1)], np.nan)
        return out


def run_world(seed: int, agent_factory: Callable[[int, np.random.RandomState], object],
              end_time: str = "10:05:00", book_log_depth: int = 1) -> WorldResult:
    cfg = rmsc04.build_config(seed=seed, date=DATE, end_time=end_time,
                              stdout_log_level="WARNING", log_orders=False,
                              book_logging=True, book_log_depth=book_log_depth)
    our_id = len(cfg["agents"])
    our_rs = np.random.RandomState(seed=(seed * 7919 + 104729) % (2 ** 32))
    agent = agent_factory(our_id, our_rs)
    cfg = config_add_agents(cfg, [agent])
    import os
    log_dir = f"p5_{os.getpid()}_{seed}_{np.random.RandomState(None).randint(1 << 30)}"
    end_state = abides.run(cfg, log_dir=log_dir, kernel_random_state=cfg["random_state_kernel"])
    agents = end_state["agents"]
    ob = agents[0].order_books[TICKER]

    n = len(ob.book_log2)
    t = np.empty(n, dtype=np.int64)
    bid = np.full(n, np.nan)
    ask = np.full(n, np.nan)
    bq = np.zeros(n)
    aq = np.zeros(n)
    for i, d in enumerate(ob.book_log2):
        t[i] = d["QuoteTime"]
        if len(d["bids"]):
            bid[i], bq[i] = d["bids"][0][0], d["bids"][0][1]
        if len(d["asks"]):
            ask[i], aq[i] = d["asks"][0][0], d["asks"][0][1]

    hold: Dict[str, int] = {}
    for ag in agents[1:]:
        k = type(ag).__name__
        hold[k] = hold.get(k, 0) + int(getattr(ag, "holdings", {}).get(TICKER, 0))

    rec = agents[our_id].record() if hasattr(agents[our_id], "record") else {}
    tx = sorted(list(ob.buy_transactions) + list(ob.sell_transactions))
    tx_t = np.array([a for a, _ in tx], dtype=np.int64)
    tx_q = np.array([b for _, b in tx], dtype=float)
    return WorldResult(seed, t, bid, ask, bq, aq, hold, rec, float(tx_q.sum()), tx_t, tx_q)
