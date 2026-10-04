"""C9 strict simulator — Amendment 1 of eval/PREREGISTRATION-walkforward-12d.md (S1, S2; snapshot ids for S3).

Differences from the frozen components/sim/fills.py (which stays the primary):
  - a leg fills against the FIRST quote published at or after its arrival (adverse bound on changes hidden inside a
    venue's publication interval), not the last one before it; no fill if that quote is > stale_cap after arrival;
  - intents with displayed size 0 at detection are not sent; outcomes come from filled quantities;
  - unwinds also use the first quote at/after the unwind time;
  - besides the frozen basis-adjusted mark, matched positions are marked at the mid of the first quote at/after
    arrival + H (markout, a self-financing mark of the short-S/long-B position);
  - the quote index each leg hit is returned (shared-liquidity collision analysis, S3).
"""
from __future__ import annotations

import numpy as np
import polars as pl

from components.sim.fills import LegBook


def at_next(b: LegBook, t: np.ndarray, cap_us: float):
    i = np.searchsorted(b.ts, t, side="left")
    ok = i < b.ts.size
    i = np.clip(i, 0, b.ts.size - 1)
    ok &= (b.ts[i] - t) <= cap_us
    return ok, i, b.bid[i], b.ask[i], b.bsz[i], b.asz[i]


def mid_next(b: LegBook, t: np.ndarray) -> np.ndarray:
    i = np.clip(np.searchsorted(b.ts, t, side="left"), 0, b.ts.size - 1)
    return 0.5 * (b.bid[i] + b.ask[i])


def simulate_strict(intents: pl.DataFrame, books: dict[str, LegBook], order_lat_us: dict[str, float], fee_bps: dict[str, float],
                    q_max: float = 0.05, stale_cap_us: float = 1e6, markouts_s: tuple[float, ...] = (1.0, 10.0)) -> pl.DataFrame:
    intents = intents.filter(pl.col("size") > 0)
    cols = ["opp_id", "outcome", "pnl_usd", "pnl_bps", "snap_s", "snap_b"] + [f"pnl_{k}_mo{h:g}" for h in markouts_s for k in ("usd", "bps")]
    if intents.height == 0:
        return pl.DataFrame(schema={c: (pl.Int64 if c in ("opp_id", "snap_s", "snap_b") else pl.Utf8 if c == "outcome" else pl.Float64) for c in cols})
    res = []
    for (sv, bv), g in intents.group_by(["sell_venue", "buy_venue"]):
        S, B = books[sv], books[bv]
        td = g["t_decide_us"].to_numpy().astype(np.float64)
        ls, lb = g["limit_sell_px"].to_numpy(), g["limit_buy_px"].to_numpy()
        q = np.minimum(g["size"].to_numpy(), q_max)
        ols, olb = order_lat_us[sv], order_lat_us[bv]
        ta_s, ta_b = td + ols, td + olb
        oks, i_s, bid_s, _, bsz_s, _ = at_next(S, ta_s, stale_cap_us)
        okb, i_b, _, ask_b, _, asz_b = at_next(B, ta_b, stale_cap_us)
        fill_s = oks & (bid_s >= ls - 1e-9) & (bsz_s > 0)
        fill_b = okb & (ask_b <= lb + 1e-9) & (asz_b > 0)
        qs = np.where(fill_s, np.minimum(q, bsz_s), 0.0)
        qb = np.where(fill_b, np.minimum(q, asz_b), 0.0)
        m = np.minimum(qs, qb)
        mid0 = 0.5 * (ls + lb)
        basis_px = g["basis0_bps"].to_numpy() * 1e-4 * mid0
        fs, fb = fee_bps[sv] * 1e-4, fee_bps[bv] * 1e-4
        fees_m = m * (fs * np.where(fill_s, bid_s, 0.0) + fb * np.where(fill_b, ask_b, 0.0))
        spread = np.where(fill_s & fill_b, bid_s - ask_b, 0.0)
        t_unw = td + 2 * max(ols, olb)
        _, _, _, ask_s2, _, _ = at_next(S, t_unw + ols, np.inf)
        _, _, bid_b2, _, _, _ = at_next(B, t_unw + olb, np.inf)
        xs, xb = qs - m, qb - m   # unmatched quantity sold on S / bought on B → bought back on S / sold back on B
        unw = (np.where(xs > 0, xs * (bid_s - ask_s2) - xs * fs * (bid_s + ask_s2), 0.0)
               + np.where(xb > 0, xb * (bid_b2 - ask_b) - xb * fb * (bid_b2 + ask_b), 0.0))
        pnl = m * (spread - basis_px) - fees_m + unw
        denom = q * mid0
        out = {"opp_id": g["opp_id"].to_numpy(),
               "outcome": np.where((qs > 0) & (qb > 0), "both", np.where(qs > 0, "sell_only", np.where(qb > 0, "buy_only", "none"))),
               "pnl_usd": pnl, "pnl_bps": pnl / denom * 1e4,
               "snap_s": np.where(fill_s, i_s, -1).astype(np.int64), "snap_b": np.where(fill_b, i_b, -1).astype(np.int64)}
        for h in markouts_s:
            ms_, mb_ = mid_next(S, ta_s + h * 1e6), mid_next(B, ta_b + h * 1e6)
            p = m * (spread - (ms_ - mb_)) - fees_m + unw
            out[f"pnl_usd_mo{h:g}"], out[f"pnl_bps_mo{h:g}"] = p, p / denom * 1e4
        res.append(pl.DataFrame(out))
    return pl.concat(res).sort("opp_id").select(cols)
