"""C8 Evaluator: predictions + labels (+ alarms, events) -> scalar metrics.

Primary scalar: prequential log-loss (proper scoring rule; lower is better). Secondary:
accuracy and AUC on non-tie labels, Brier, gross mid-to-mid edge (bps per signal), event-
window log-loss, alarm counts, latency percentiles, and moving-block-bootstrap confidence
intervals for log-loss differences (blocks absorb serial dependence between overlapping labels).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import roc_auc_score

EPS = 1e-12


def pointwise_logloss(p: np.ndarray, y: np.ndarray) -> np.ndarray:
    p = np.clip(p, EPS, 1 - EPS)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


def score(p: np.ndarray, y: np.ndarray, move_bps: np.ndarray | None = None, mask: np.ndarray | None = None) -> dict:
    m = ~np.isnan(y)
    if mask is not None:
        m &= mask
    if m.sum() < 10:
        return {"n": int(m.sum())}
    pp, yy = p[m], y[m]
    out = {
        "n": int(m.sum()),
        "logloss": float(pointwise_logloss(pp, yy).mean()),
        "acc": float(((pp > 0.5) == (yy > 0.5)).mean()),
        "brier": float(((pp - yy) ** 2).mean()),
        "auc": float(roc_auc_score(yy, pp)) if 0 < yy.mean() < 1 else float("nan"),
        "base_rate": float(yy.mean()),
    }
    if move_bps is not None:
        s = np.sign(pp - 0.5)
        out["edge_bps"] = float((s * move_bps[m]).mean())
    return out


def block_bootstrap_ci(d: np.ndarray, block: int = 600, n_boot: int = 1000, seed: int = 0) -> tuple[float, float, float]:
    """Moving-block bootstrap 95% CI of mean(d) (d = per-step loss differences)."""
    d = d[~np.isnan(d)]
    n = len(d)
    if n < 2 * block:
        return float(d.mean()), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    nb = int(np.ceil(n / block))
    starts = rng.integers(0, n - block + 1, size=(n_boot, nb))
    csum = np.concatenate([[0.0], np.cumsum(d)])
    sums = (csum[starts + block] - csum[starts]).sum(1)
    means = sums / (nb * block)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(d.mean()), float(lo), float(hi)


def latency_summary(ns: np.ndarray) -> dict:
    us = ns / 1000.0
    return {"p50_us": float(np.percentile(us, 50)), "p99_us": float(np.percentile(us, 99)),
            "p999_us": float(np.percentile(us, 99.9)), "max_us": float(us.max())}


def detection_report(alarm_steps: list[int], grid_us: np.ndarray, events_us: list[int],
                     tol_after_s: int = 1800) -> dict:
    """Alarms within [event, event + tol] count as detections; all others are false alarms."""
    a_us = np.array([grid_us[s] for s in alarm_steps], dtype=np.int64)
    hit, delays = np.zeros(len(a_us), bool), []
    for e in events_us:
        inw = (a_us >= e) & (a_us <= e + tol_after_s * 1_000_000)
        hit |= inw
        if inw.any():
            delays.append(float((a_us[inw].min() - e) / 1e6))
    return {"n_alarms": int(len(a_us)), "n_false": int((~hit).sum()), "n_events": len(events_us),
            "n_detected": len(delays), "delays_s": delays}


def day_cluster_bootstrap_ci(d: np.ndarray, day_ids: np.ndarray, n_boot: int = 2000, seed: int = 0,
                             levels: tuple[float, ...] = (95.0, 97.5)) -> dict:
    """Paired bootstrap over *days*: resample whole days with replacement and recompute the
    pooled mean of per-step differences d. Days are the independent units; within-day serial
    dependence (overlapping labels, volatility clustering) is kept intact."""
    m = ~np.isnan(d)
    d, day_ids = d[m], day_ids[m]
    days = np.unique(day_ids)
    sums = np.array([d[day_ids == k].sum() for k in days])
    ns = np.array([(day_ids == k).sum() for k in days], dtype=float)
    rng = np.random.default_rng(seed)
    pick = rng.integers(0, len(days), size=(n_boot, len(days)))
    means = sums[pick].sum(1) / ns[pick].sum(1)
    out = {"mean": float(sums.sum() / ns.sum()), "n_days": int(len(days))}
    for lv in levels:
        lo, hi = np.percentile(means, [(100 - lv) / 2, 100 - (100 - lv) / 2])
        out[f"ci{lv:g}"] = [float(lo), float(hi)]
    out["days_better"] = int((sums / ns < 0).sum())
    return out


@dataclass
class ExecArrays:
    """Top-of-book at decision time + delay (entry) and at horizon + delay (exit), per grid step."""
    delay_ms: int
    mid: np.ndarray
    bid_in: np.ndarray
    ask_in: np.ndarray
    bid_out: np.ndarray
    ask_out: np.ndarray


def exec_arrays(recv_us: np.ndarray, bid0: np.ndarray, ask0: np.ndarray, grid_us: np.ndarray,
                mid: np.ndarray, h_steps: int, step_us: int, delay_ms: int) -> ExecArrays:
    """As-of joins on receive time: the order goes out `delay_ms` after the decision and fills
    against the book then (taker); the exit happens `delay_ms` after the horizon ends."""
    dt = delay_ms * 1000
    T = grid_us.shape[0]
    i_in = np.searchsorted(recv_us, grid_us + dt, side="right") - 1
    i_out = np.searchsorted(recv_us, grid_us + h_steps * step_us + dt, side="right") - 1
    out_ok = (np.arange(T) + h_steps < T)  # exit must fall inside the same day's grid
    nan = np.full(T, np.nan)
    bo, ao = nan.copy(), nan.copy()
    bo[out_ok], ao[out_ok] = bid0[i_out[out_ok]], ask0[i_out[out_ok]]
    return ExecArrays(delay_ms, mid, bid0[i_in], ask0[i_in], bo, ao)


def trading_edge(p: np.ndarray, ex: ExecArrays, move_bps: np.ndarray, mask: np.ndarray | None = None) -> dict:
    """Per-signal edge in basis points of mid, for d = sign(p - 0.5) on every step (ties included).

    gross_mid: d * mid-to-mid move. taker: buy at ask / sell at bid on entry and exit (pays the
    spread twice, i.e. ~one full spread per round trip vs mid). Fees are subtracted by the caller
    (2 x fee per round trip). break_even_fee_per_side = taker / 2.
    """
    d = np.sign(p - 0.5)
    ok = (d != 0) & ~np.isnan(move_bps) & ~np.isnan(ex.bid_out)
    if mask is not None:
        ok &= mask
    long_ = (ex.bid_out - ex.ask_in) / ex.mid * 1e4
    short = (ex.bid_in - ex.ask_out) / ex.mid * 1e4
    taker = np.where(d > 0, long_, short)
    # Maker upper bound: both legs filled passively at the touch (long: bid in, ask out).
    maker = np.where(d > 0, (ex.ask_out - ex.bid_in) / ex.mid * 1e4, (ex.ask_in - ex.bid_out) / ex.mid * 1e4)
    spread_bps = (ex.ask_in - ex.bid_in) / ex.mid * 1e4
    n = int(ok.sum())
    if n == 0:
        return {"n": 0}
    return {"n": n, "gross_mid_bps": float((d * move_bps)[ok].mean()), "taker_bps": float(taker[ok].mean()),
            "maker_ub_bps": float(maker[ok].mean()),
            "spread_bps": float(spread_bps[ok].mean()), "break_even_fee_per_side_bps": float(taker[ok].mean() / 2)}
