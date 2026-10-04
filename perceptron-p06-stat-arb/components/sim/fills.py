"""C9 sim — latency-injected fills against exchange-time truth.

Each leg is an IOC limit order at the price we *observed*. It reaches venue v at exchange time
t_decide + order_latency[v] and fills (up to the top-of-book size then) only if the venue's price
at that instant is at or better than our limit. Leg mismatch is unwound on the same venue at the
top of book a further 2·max(order latency) later (we must first learn the other leg failed), paying
the taker fee again. P&L is marked against the fair basis observed at decision time.
Assumption (labelled): inventory is pre-positioned on every venue, so no transfers are needed.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import polars as pl


@dataclass
class LegBook:
    ts: np.ndarray      # exchange timestamps, sorted
    bid: np.ndarray
    ask: np.ndarray
    bsz: np.ndarray
    asz: np.ndarray

    def at(self, t: np.ndarray) -> tuple[np.ndarray, ...]:
        i = np.searchsorted(self.ts, t, side="right") - 1
        ok = i >= 0
        i = np.clip(i, 0, len(self.ts) - 1)
        return ok, self.bid[i], self.ask[i], self.bsz[i], self.asz[i]


def truth_books(q: pl.DataFrame) -> dict[str, LegBook]:
    out = {}
    for (leg,), g in q.sort("ts_exch_us", maintain_order=True).group_by(["leg"], maintain_order=True):
        out[leg] = LegBook(g["ts_exch_us"].to_numpy(), g["bid_px"].to_numpy(), g["ask_px"].to_numpy(),
                           g["bid_sz"].to_numpy(), g["ask_sz"].to_numpy())
    return out


def simulate(intents: pl.DataFrame, books: dict[str, LegBook], order_lat_us: dict[str, float], fee_bps: dict[str, float],
             q_max: float = 0.05) -> pl.DataFrame:
    """intents: rows with opp_id, t_decide_us, sell_venue, buy_venue, limit_sell_px, limit_buy_px, size, basis0_bps."""
    if intents.height == 0:
        return intents.with_columns(pl.lit(None).alias("outcome"), pl.lit(0.0).alias("pnl_usd"), pl.lit(0.0).alias("pnl_bps"))
    res = []
    for (sv, bv), g in intents.group_by(["sell_venue", "buy_venue"]):
        S, B = books[sv], books[bv]
        td = g["t_decide_us"].to_numpy().astype(np.float64)
        ls, lbp = g["limit_sell_px"].to_numpy(), g["limit_buy_px"].to_numpy()
        q = np.minimum(np.maximum(g["size"].to_numpy(), 0.0), q_max)
        q = np.where(q <= 0, q_max, q)  # size unknown → trade the cap
        ols, olb = order_lat_us[sv], order_lat_us[bv]
        oks, bid_s, _, bsz_s, _ = S.at(td + ols)
        okb, _, ask_b, _, asz_b = B.at(td + olb)
        fill_s = oks & (bid_s >= ls - 1e-9)
        fill_b = okb & (ask_b <= lbp + 1e-9)
        qs = np.where(fill_s, np.minimum(q, bsz_s), 0.0)
        qb = np.where(fill_b, np.minimum(q, asz_b), 0.0)
        m = np.minimum(qs, qb)
        mid = 0.5 * (ls + lbp)
        basis_px = g["basis0_bps"].to_numpy() * 1e-4 * mid
        fs, fb = fee_bps[sv] * 1e-4, fee_bps[bv] * 1e-4
        pnl = m * ((bid_s - ask_b) - basis_px) - m * (fs * bid_s + fb * ask_b)
        # unwind mismatched quantity on the same venue after learning the other leg failed
        t_unw = td + 2 * max(ols, olb)
        xs = qs - m   # sold too much on S → buy back on S
        xb = qb - m   # bought too much on B → sell back on B
        _, _, ask_s2, _, _ = S.at(t_unw + ols)
        _, bid_b2, _, _, _ = B.at(t_unw + olb)
        pnl += xs * (bid_s - ask_s2) - xs * fs * (bid_s + ask_s2)
        pnl += xb * (bid_b2 - ask_b) - xb * fb * (bid_b2 + ask_b)
        outcome = np.where(fill_s & fill_b, "both", np.where(fill_s, "sell_only", np.where(fill_b, "buy_only", "none")))
        res.append(g.select("opp_id").with_columns(
            pl.Series("outcome", outcome), pl.Series("pnl_usd", pnl), pl.Series("pnl_bps", pnl / (q * mid) * 1e4),
            pl.Series("q", q)))
    return pl.concat(res).sort("opp_id")
