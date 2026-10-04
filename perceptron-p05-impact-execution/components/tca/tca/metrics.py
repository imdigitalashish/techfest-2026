"""Transaction-cost analysis with an exact counterfactual decomposition.

For a SELL (sign s=+1; BUY s=-1), each fill at price p, placed by a decision at time t_d:
    s*(P_arr - p) = s*(P_arr - m_twin(t_d))     drift: the market move that happens without us
                  + s*(m_twin(t_d) - m(t_d))    own impact: displacement caused by our earlier trades
                  + s*(m(t_d) - p)              instantaneous: spread + book walking vs the mid we saw
P_arr is the mid at the start of the window (identical in both arms by construction).
m is the treatment-arm mid; m_twin is the null-twin mid on the same seed.
"""
from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

import numpy as np


def _sign(side: str) -> float:
    return 1.0 if side == "SELL" else -1.0


def implementation_shortfall(fills: Sequence[Tuple[int, int, int]], arrival_mid: float, side: str) -> Dict:
    q = np.array([f[2] for f in fills], dtype=float)
    p = np.array([f[1] for f in fills], dtype=float)
    Q = q.sum()
    if Q <= 0:
        return dict(qty=0.0, avg_px=np.nan, is_cents=np.nan, is_bps=np.nan)
    avg = float((p * q).sum() / Q)
    is_c = _sign(side) * (arrival_mid - avg)
    return dict(qty=float(Q), avg_px=avg, is_cents=is_c, is_bps=1e4 * is_c / arrival_mid)


def decompose_is(fills, decision_times: Sequence[int], arrival_mid: float, side: str,
                 treat, twin) -> Dict:
    """Quantity-weighted IS components in bps (they sum to IS exactly)."""
    if not fills:
        return dict(drift_bps=np.nan, own_impact_bps=np.nan, instant_bps=np.nan)
    s = _sign(side)
    dts = np.asarray(sorted(decision_times), dtype=np.int64)
    ft = np.array([f[0] for f in fills], dtype=np.int64)
    fp = np.array([f[1] for f in fills], dtype=float)
    fq = np.array([f[2] for f in fills], dtype=float)
    k = np.clip(np.searchsorted(dts, ft, side="right") - 1, 0, len(dts) - 1)
    td = dts[k]
    m = treat.mid_at(td)
    mt = twin.mid_at(td)
    w = fq / fq.sum()
    f = 1e4 / arrival_mid
    drift = s * (arrival_mid - mt)
    own = s * (mt - m)
    inst = s * (m - fp)
    return dict(drift_bps=float(f * (w * drift).sum()), own_impact_bps=float(f * (w * own).sum()),
                instant_bps=float(f * (w * inst).sum()))


def decompose_fill_time(fills, decision_times: Sequence[int], arrival_mid: float, side: str, treat) -> Dict:
    """Split the decision-time cost term into delay + at-fill cost (reviews sol #2, astra #5).

    delay   = s*(m(t_d) - m(t_f-))   mid move between decision and fill (passive fills: timing / adverse selection)
    at_fill = s*(m(t_f-) - p)         execution price vs the mid just before the fill
    delay + at_fill = s*(m(t_d) - p), the "instant" term of decompose_is.
    """
    if not fills:
        return dict(delay_bps=np.nan, at_fill_bps=np.nan)
    s = _sign(side)
    dts = np.asarray(sorted(decision_times), dtype=np.int64)
    ft = np.array([f[0] for f in fills], dtype=np.int64)
    fp = np.array([f[1] for f in fills], dtype=float)
    fq = np.array([f[2] for f in fills], dtype=float)
    k = np.clip(np.searchsorted(dts, ft, side="right") - 1, 0, len(dts) - 1)
    md = treat.mid_at(dts[k])
    mf = treat.mid_at(ft, strictly_before=True)
    w = fq / fq.sum()
    f = 1e4 / arrival_mid
    return dict(delay_bps=float(f * (w * s * (md - mf)).sum()), at_fill_bps=float(f * (w * s * (mf - fp)).sum()))


def pre_window_exact(treat, twin, start_ns: int) -> bool:
    """Event-level identity of the logged top-of-book before start_ns (review sol #5, astra #4)."""
    a, b = treat.t < start_ns, twin.t < start_ns
    if a.sum() != b.sum():
        return False
    return bool(np.array_equal(treat.t[a], twin.t[b])
                and all(np.array_equal(getattr(treat, x)[a], getattr(twin, x)[b], equal_nan=True)
                        for x in ("bid", "ask", "bid_q", "ask_q")))


def impact_path(treat, twin, grid_ns: np.ndarray, side: str) -> np.ndarray:
    """Own-impact path in cents, sign-adjusted (positive = price moved against us)."""
    return _sign(side) * (twin.mid_at(grid_ns) - treat.mid_at(grid_ns))
