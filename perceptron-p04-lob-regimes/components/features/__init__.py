"""C2 Features: BookDay -> FeatureFrame on a fixed receive-time grid.

Every feature at grid time g uses only messages with recv_us <= g (as-of join with
side='right'), plus trailing windows over past grid steps. tests/test_causality.py
checks this by perturbing the future and asserting the past is unchanged.

Feature families (sources in research/components/features.md):
- Order-flow imbalance (Cont, Kukanov & Stoikov 2014), per level (multi-level OFI, Xu et al.),
  summed over trailing windows and divided by trailing average depth (depth-normalised,
  motivated by CKS's finding that the OFI price-impact coefficient scales inversely with depth).
- Queue imbalance at level 1 (Gould & Bonart 2016) and depth imbalance over 5 levels.
- Micro-price deviation (Stoikov 2018), spread in ticks, log depth.
- Past mid returns, realised volatility, message intensity.
"""
from __future__ import annotations

import numpy as np

from components.contracts import TICK_SIZE, BookDay, FeatureFrame

SEC = 1_000_000
OFI_WINDOWS_S = (1, 5, 30)
RET_WINDOWS_S = (1, 5, 30)
RV_WINDOWS_S = (60, 600)
DEPTH_NORM_WINDOW_S = 300
WARMUP_S = 600  # first grid steps without full lookback are dropped


def _level_ofi(bp: np.ndarray, bs: np.ndarray, ap: np.ndarray, as_: np.ndarray) -> np.ndarray:
    """Per-message OFI contribution e_n (Cont, Kukanov & Stoikov 2014, eq. 2) for one level."""
    e = np.zeros_like(bp)
    bp0, bs0, ap0, as0 = bp[:-1], bs[:-1], ap[:-1], as_[:-1]
    bp1, bs1, ap1, as1 = bp[1:], bs[1:], ap[1:], as_[1:]
    e[1:] = ((bp1 >= bp0) * bs1 - (bp1 <= bp0) * bs0
             - (ap1 <= ap0) * as1 + (ap1 >= ap0) * as0)
    return e


def _trailing_sum(x: np.ndarray, w: int) -> np.ndarray:
    c = np.concatenate([[0.0], np.cumsum(x)])
    out = np.empty_like(x)
    idx = np.arange(len(x))
    lo = np.maximum(idx + 1 - w, 0)
    out[:] = c[idx + 1] - c[lo]
    return out


def _trailing_mean(x: np.ndarray, w: int) -> np.ndarray:
    n = np.minimum(np.arange(len(x)) + 1, w)
    return _trailing_sum(x, w) / n


def build_features(book: BookDay, step_s: float = 1.0, drop_warmup: bool = True) -> FeatureFrame:
    step_us = int(step_s * SEC)
    tick = TICK_SIZE[book.symbol]
    day_start = (book.recv_us[0] // (86400 * SEC)) * 86400 * SEC
    grid = np.arange(day_start + step_us, day_start + 86400 * SEC + 1, step_us, dtype=np.int64)
    pos = np.searchsorted(book.recv_us, grid, side="right") - 1  # last message with recv <= g
    valid = pos >= 0
    grid, pos = grid[valid], pos[valid]
    steps_per_s = 1.0 / step_s
    ws = lambda s: max(1, int(round(s * steps_per_s)))

    bp, bs, ap, as_ = book.bid_px, book.bid_sz, book.ask_px, book.ask_sz
    b0, a0, qb, qa = bp[pos, 0], ap[pos, 0], bs[pos, 0], as_[pos, 0]
    mid = 0.5 * (b0 + a0)
    spread_ticks = np.round((a0 - b0) / tick, 6)
    micro = (a0 * qb + b0 * qa) / np.maximum(qb + qa, 1e-12)
    depth5 = bs[pos].sum(1) + as_[pos].sum(1)

    feats: dict[str, np.ndarray] = {}
    feats["spread_ticks"] = spread_ticks
    feats["qi1"] = (qb - qa) / np.maximum(qb + qa, 1e-12)
    feats["di5"] = (bs[pos].sum(1) - as_[pos].sum(1)) / np.maximum(depth5, 1e-12)
    feats["micro_dev_ticks"] = (micro - mid) / tick
    feats["log_depth5"] = np.log(np.maximum(depth5, 1e-9))

    # Cumulative OFI per message, read at grid positions -> windowed sums by differencing.
    depth_avg = _trailing_mean(depth5 / 10.0, ws(DEPTH_NORM_WINDOW_S))  # avg size per level-side
    ofi_l1 = np.cumsum(_level_ofi(bp[:, 0], bs[:, 0], ap[:, 0], as_[:, 0]))[pos]
    ofi_ml = np.cumsum(sum(_level_ofi(bp[:, i], bs[:, i], ap[:, i], as_[:, i]) for i in range(bp.shape[1])))[pos]
    for w in OFI_WINDOWS_S:
        k = ws(w)
        for name, c in (("ofi1", ofi_l1), ("ofi5", ofi_ml)):
            d = np.empty_like(c)
            d[k:] = c[k:] - c[:-k]
            d[:k] = c[:k] - c[0]
            feats[f"{name}_{w}s_n"] = d / np.maximum(depth_avg, 1e-9)

    logmid = np.log(mid)
    for w in RET_WINDOWS_S:
        k = ws(w)
        r = np.zeros_like(logmid)
        r[k:] = logmid[k:] - logmid[:-k]
        feats[f"ret_{w}s_bps"] = r * 1e4
    r1 = np.zeros_like(logmid)
    r1[1:] = np.diff(logmid) * 1e4
    for w in RV_WINDOWS_S:
        feats[f"rv_{w}s_bps"] = np.sqrt(_trailing_sum(r1 * r1, ws(w)))
    k10 = ws(10)
    nmsg = np.zeros_like(mid)
    nmsg[k10:] = pos[k10:] - pos[:-k10]
    feats["log_msgs_10s"] = np.log1p(nmsg)

    names = tuple(feats)
    X = np.column_stack([feats[n] for n in names]).astype(np.float64)
    start = ws(WARMUP_S) if drop_warmup else 0
    return FeatureFrame(book.symbol, book.day, step_us, grid[start:], names, X[start:], mid[start:],
                        spread_ticks[start:])
