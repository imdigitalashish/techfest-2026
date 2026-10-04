"""C8 Evaluator: predictions + labels (+ alarms, events) -> scalar metrics.

Primary scalar: prequential log-loss (proper scoring rule; lower is better). Secondary:
accuracy and AUC on non-tie labels, Brier, gross mid-to-mid edge (bps per signal), event-
window log-loss, alarm counts, latency percentiles, and moving-block-bootstrap confidence
intervals for log-loss differences (blocks absorb serial dependence between overlapping labels).
"""
from __future__ import annotations

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
