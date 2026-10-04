"""C8 decision — policies that turn opportunities into order intents.

  naive          act on every opportunity whose edge beats both taker fees
  threshold      act when net edge > θ*, θ* tuned on the training day (global)
  threshold_pair act when net edge > θ*[pair], tuned per ordered venue pair (strong baseline)
  ev_*           act when EV = S(L|x)·net − (1 − S(L|x))·λ > 0          (spike v0)
  ev_wait_*      Δ* = argmax_Δ S(Δ+L)·net − (S(Δ) − S(Δ+L))·λ; act at Δ* if still visible
  lev            act when the learned executable value E[PnL | x, L] > 0 (spike v1, lev.py)
L = end-to-end latency (feed + compute + order); λ = mean loss of a failed attempt, estimated on
the training day by the simulator. Times in µs unless suffixed _ms.
"""
from __future__ import annotations

import numpy as np
import polars as pl

from components.costs.fees import leg_venue, taker_bps
from components.decay.survival import model_X

WAIT_GRID_MS = np.array([0.0, 0.5, 1, 2, 5, 10, 20, 50], dtype=float)


def with_net(opp: pl.DataFrame, tier: str) -> pl.DataFrame:
    fee_s = opp["sell_venue"].map_elements(lambda l: taker_bps(leg_venue(l), tier), return_dtype=pl.Float64)
    fee_b = opp["buy_venue"].map_elements(lambda l: taker_bps(leg_venue(l), tier), return_dtype=pl.Float64)
    return opp.with_columns((pl.col("edge0_bps") - fee_s - fee_b).alias("net0_bps"))


def intents(opp: pl.DataFrame, act: np.ndarray, t_decide: np.ndarray, score: np.ndarray, policy: str) -> pl.DataFrame:
    act = np.asarray(act, dtype=bool)
    return opp.filter(pl.Series(act)).with_columns(
        pl.Series("t_decide_us", np.asarray(t_decide)[act].astype(np.int64)), pl.Series("score", np.asarray(score, dtype=float)[act]),
        pl.lit(policy).alias("policy"))


def naive(opp: pl.DataFrame, compute_us: float) -> pl.DataFrame:
    net = opp["net0_bps"].to_numpy()
    return intents(opp, net > 0, opp["t_obs_us"].to_numpy() + compute_us, net, "naive")


def threshold(opp: pl.DataFrame, compute_us: float, theta_bps: float) -> pl.DataFrame:
    net = opp["net0_bps"].to_numpy()
    return intents(opp, net > theta_bps, opp["t_obs_us"].to_numpy() + compute_us, net, "threshold")


def threshold_pair(opp: pl.DataFrame, compute_us: float, theta: dict[float, float]) -> pl.DataFrame:
    net = opp["net0_bps"].to_numpy()
    th = np.array([theta.get(float(p), np.inf) for p in opp["pair_id"].to_numpy()])
    return intents(opp, net > th, opp["t_obs_us"].to_numpy() + compute_us, net, "threshold_pair")


def _s_at(model, X: np.ndarray, t_ms: np.ndarray) -> np.ndarray:
    """Row-wise S(t_i | x_i)."""
    t_ms = np.broadcast_to(np.asarray(t_ms, dtype=float), (X.shape[0],))
    if model.kind == "km":
        return model.survival(t_ms, None)[0] if np.unique(t_ms).size == 1 else np.array(
            [model.survival(np.array([t]), None)[0, 0] for t in t_ms])
    if model.kind == "km_pair":
        return model.s_rowwise(X, t_ms)
    Z = (X - model.mu) / model.sd
    lam = np.exp(Z @ model.beta[:-1] + model.beta[-1])
    return np.exp(-np.power(np.maximum(t_ms, 1e-6) / lam, model.rho))


def ev(opp: pl.DataFrame, model, L_us: np.ndarray, lam_bps: float, compute_us: float, name: str = "ev") -> pl.DataFrame:
    X = model_X(model, opp)
    net = opp["net0_bps"].to_numpy()
    S = _s_at(model, X, np.asarray(L_us) / 1000.0)
    score = S * net - (1 - S) * lam_bps
    return intents(opp, (score > 0) & (net > 0), opp["t_obs_us"].to_numpy() + compute_us, score, name)


def ev_wait(opp: pl.DataFrame, model, L_us: np.ndarray, lam_bps: float, compute_us: float, name: str = "ev_wait") -> pl.DataFrame:
    """Chooses a confirmation delay per opportunity; the runner re-reads observed prices at t_decide."""
    X = model_X(model, opp)
    net = opp["net0_bps"].to_numpy()
    L_ms = np.asarray(L_us) / 1000.0
    best = np.full(len(net), -np.inf); best_d = np.zeros(len(net))
    for d in WAIT_GRID_MS:
        s_d = _s_at(model, X, np.full(len(net), d)) if d > 0 else np.ones(len(net))
        s_dl = _s_at(model, X, d + L_ms)
        val = s_dl * net - (s_d - s_dl) * lam_bps
        upd = val > best
        best[upd] = val[upd]; best_d[upd] = d
    wait_us = best_d * 1000.0
    visible = opp["duration_obs_us"].to_numpy() > wait_us
    act = (best > 0) & (net > 0) & visible
    out = intents(opp, act, opp["t_obs_us"].to_numpy() + wait_us + compute_us, best, name)
    return out.with_columns(pl.Series("wait_us", wait_us[act]))


def lev(opp: pl.DataFrame, model, L_us: float, compute_us: float, margin_bps: float = 0.0) -> pl.DataFrame:
    pred = model.predict(opp, L_us)
    net = opp["net0_bps"].to_numpy()
    return intents(opp, (pred > margin_bps) & (net > 0), opp["t_obs_us"].to_numpy() + compute_us, pred, "lev")
