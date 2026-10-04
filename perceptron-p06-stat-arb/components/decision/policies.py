"""C8 decision — policies that turn opportunities into order intents.

  naive      act on every opportunity whose edge beats both taker fees
  threshold  act when net edge > θ*, θ* tuned on the training day (the "statistical model" baseline)
  ev         act when EV = S(L|x)·net − (1 − S(L|x))·λ > 0          (spike v0)
  ev_wait    pick Δ* = argmax_Δ S(Δ+L)·net − (S(Δ) − S(Δ+L))·λ; act at Δ* if the
             opportunity is still visible then                         (spike v0, act-now-vs-wait)
L = end-to-end latency (feed + compute + order); λ = mean loss of a failed attempt, estimated on
the training day by the simulator. All times in µs unless suffixed _ms.
"""
from __future__ import annotations

import numpy as np
import polars as pl

from components.costs.fees import leg_venue, taker_bps
from components.decay.survival import FEATURES, DecayModel

WAIT_GRID_MS = np.array([0.0, 0.5, 1, 2, 5, 10, 20, 50], dtype=float)


def with_net(opp: pl.DataFrame, tier: str) -> pl.DataFrame:
    fee_s = opp["sell_venue"].map_elements(lambda l: taker_bps(leg_venue(l), tier), return_dtype=pl.Float64)
    fee_b = opp["buy_venue"].map_elements(lambda l: taker_bps(leg_venue(l), tier), return_dtype=pl.Float64)
    return opp.with_columns((pl.col("edge0_bps") - fee_s - fee_b).alias("net0_bps"))


def intents(opp: pl.DataFrame, act: np.ndarray, t_decide: np.ndarray, score: np.ndarray, policy: str) -> pl.DataFrame:
    return opp.filter(pl.Series(act)).with_columns(
        pl.Series("t_decide_us", t_decide[act].astype(np.int64)), pl.Series("score", score[act]), pl.lit(policy).alias("policy"))


def naive(opp: pl.DataFrame, compute_us: float) -> pl.DataFrame:
    net = opp["net0_bps"].to_numpy()
    return intents(opp, net > 0, opp["t_obs_us"].to_numpy() + compute_us, net, "naive")


def threshold(opp: pl.DataFrame, compute_us: float, theta_bps: float) -> pl.DataFrame:
    net = opp["net0_bps"].to_numpy()
    return intents(opp, net > theta_bps, opp["t_obs_us"].to_numpy() + compute_us, net, f"threshold")


def ev(opp: pl.DataFrame, model: DecayModel, L_us: np.ndarray, lam_bps: float, compute_us: float) -> pl.DataFrame:
    X = opp.select(FEATURES).to_numpy()
    net = opp["net0_bps"].to_numpy()
    S = _s_at(model, X, L_us / 1000.0)
    score = S * net - (1 - S) * lam_bps
    return intents(opp, (score > 0) & (net > 0), opp["t_obs_us"].to_numpy() + compute_us, score, "ev")


def ev_wait(opp: pl.DataFrame, model: DecayModel, L_us: np.ndarray, lam_bps: float, compute_us: float) -> pl.DataFrame:
    """Chooses a confirmation delay per opportunity. The simulator re-reads observed prices at t_decide."""
    X = opp.select(FEATURES).to_numpy()
    net = opp["net0_bps"].to_numpy()
    L_ms = L_us / 1000.0
    best = np.full(len(net), -np.inf); best_d = np.zeros(len(net))
    for d in WAIT_GRID_MS:
        s_d = _s_at(model, X, np.full(len(net), d)) if d > 0 else np.ones(len(net))
        s_dl = _s_at(model, X, d + L_ms)
        val = s_dl * net - (s_d - s_dl) * lam_bps
        upd = val > best
        best[upd] = val[upd]; best_d[upd] = d
    wait_us = best_d * 1000.0
    visible = opp["duration_obs_us"].to_numpy() > wait_us      # still open (as observed) when we act
    act = (best > 0) & (net > 0) & visible
    out = intents(opp, act, opp["t_obs_us"].to_numpy() + wait_us + compute_us, best, "ev_wait")
    return out.with_columns(pl.Series("wait_us", wait_us[act]))


def _s_at(model: DecayModel, X: np.ndarray, t_ms: np.ndarray) -> np.ndarray:
    """Row-wise S(t_i | x_i)."""
    if model.kind == "km":
        return model.survival(np.asarray(t_ms), None)[0]
    Z = (X - model.mu) / model.sd
    lam = np.exp(Z @ model.beta[:-1] + model.beta[-1])
    return np.exp(-np.power(np.maximum(t_ms, 1e-6) / lam, model.rho))
