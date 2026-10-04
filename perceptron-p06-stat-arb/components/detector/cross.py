"""C6 detector (with the C4 EWMA fair-basis baseline inlined for speed).

Event loop over a merged quote stream sorted by the *observer's* clock. For every ordered leg
pair (sell s at its bid, buy b at its ask) it tracks
    edge_bps = (bid_s - ask_b) / ref * 1e4 - basis_sb
where basis_sb is an exponentially weighted fair mid difference (no look-ahead: it is updated only
with past and current observations). An episode opens when edge > theta and closes when
edge <= theta; it is censored if the counter-leg's quote is older than max_age (feed gap) or the
data ends.
"""
from __future__ import annotations

import numpy as np
import polars as pl
from numba import njit

from architecture.contracts.frames import OPPORTUNITY_FRAME


@njit(cache=True)
def _detect(t, leg, bid, ask, bsz, asz, n_leg, theta, basis_tau_us, warmup_us, max_age_us, cap):
    lb = np.full(n_leg, np.nan); la = np.full(n_leg, np.nan)
    lbs = np.zeros(n_leg); las = np.zeros(n_leg)
    lt = np.full(n_leg, -1, np.int64)
    vol = np.zeros(n_leg)
    basis = np.zeros((n_leg, n_leg)); bt = np.full((n_leg, n_leg), -1, np.int64)
    is_open = np.zeros((n_leg, n_leg), np.bool_)
    t0 = np.zeros((n_leg, n_leg), np.int64)
    e0 = np.zeros((n_leg, n_leg)); emax = np.zeros((n_leg, n_leg))
    ages = np.zeros((n_leg, n_leg), np.int64); ageb = np.zeros((n_leg, n_leg), np.int64)
    sprs = np.zeros((n_leg, n_leg)); sprb = np.zeros((n_leg, n_leg))
    sz0 = np.zeros((n_leg, n_leg)); vol0 = np.zeros((n_leg, n_leg)); upd_sell = np.zeros((n_leg, n_leg), np.bool_)
    lim_s = np.zeros((n_leg, n_leg)); lim_b = np.zeros((n_leg, n_leg)); bas0 = np.zeros((n_leg, n_leg))

    o_t0 = np.empty(cap, np.int64); o_t1 = np.empty(cap, np.int64)
    o_s = np.empty(cap, np.int32); o_b = np.empty(cap, np.int32)
    o_e0 = np.empty(cap); o_emax = np.empty(cap)
    o_ages = np.empty(cap, np.int64); o_ageb = np.empty(cap, np.int64)
    o_sprs = np.empty(cap); o_sprb = np.empty(cap); o_sz = np.empty(cap); o_vol = np.empty(cap)
    o_cens = np.empty(cap, np.bool_); o_upd = np.empty(cap, np.bool_)
    o_lims = np.empty(cap); o_limb = np.empty(cap); o_bas = np.empty(cap)
    k = 0
    tfirst = t[0]
    for i in range(t.shape[0]):
        v = leg[i]; ti = t[i]
        if lt[v] >= 0:
            om = 0.5 * (lb[v] + la[v]); nm = 0.5 * (bid[i] + ask[i])
            a = 1.0 - np.exp(-max(ti - lt[v], 1) / 1e6)
            vol[v] = (1 - a) * vol[v] + a * abs(nm - om) / nm * 1e4
        lb[v] = bid[i]; la[v] = ask[i]; lbs[v] = bsz[i]; las[v] = asz[i]; lt[v] = ti
        mv = 0.5 * (bid[i] + ask[i])
        warm = (ti - tfirst) > warmup_us
        for u in range(n_leg):
            if u == v or lt[u] < 0:
                continue
            mu = 0.5 * (lb[u] + la[u]); ref = 0.5 * (mv + mu)
            lo = min(u, v); hi = max(u, v)
            d = (mv - mu) / ref * 1e4
            dlh = d if v == lo else -d
            if bt[lo, hi] < 0:
                basis[lo, hi] = dlh
            else:
                a = 1.0 - np.exp(-max(ti - bt[lo, hi], 1) / basis_tau_us)
                basis[lo, hi] += a * (dlh - basis[lo, hi])
            bt[lo, hi] = ti
            b_vu = basis[lo, hi] if v == lo else -basis[lo, hi]  # fair (mid_v - mid_u) in bps
            stale = (ti - lt[u]) > max_age_us
            for side in range(2):
                if side == 0:
                    s = v; b = u; e = (lb[v] - la[u]) / ref * 1e4 - b_vu; bas = b_vu
                else:
                    s = u; b = v; e = (lb[u] - la[v]) / ref * 1e4 + b_vu; bas = -b_vu
                if is_open[s, b]:
                    if e > emax[s, b]:
                        emax[s, b] = e
                    if e <= theta or stale:
                        if k < cap:
                            o_t0[k] = t0[s, b]; o_t1[k] = ti; o_s[k] = s; o_b[k] = b; o_e0[k] = e0[s, b]; o_emax[k] = emax[s, b]
                            o_ages[k] = ages[s, b]; o_ageb[k] = ageb[s, b]; o_sprs[k] = sprs[s, b]; o_sprb[k] = sprb[s, b]
                            o_sz[k] = sz0[s, b]; o_vol[k] = vol0[s, b]; o_cens[k] = stale; o_upd[k] = upd_sell[s, b]
                            o_lims[k] = lim_s[s, b]; o_limb[k] = lim_b[s, b]; o_bas[k] = bas0[s, b]
                            k += 1
                        is_open[s, b] = False
                elif warm and (not stale) and e > theta:
                    is_open[s, b] = True; t0[s, b] = ti; e0[s, b] = e; emax[s, b] = e
                    ages[s, b] = ti - lt[s]; ageb[s, b] = ti - lt[b]
                    sprs[s, b] = (la[s] - lb[s]) / ref * 1e4; sprb[s, b] = (la[b] - lb[b]) / ref * 1e4
                    sz0[s, b] = min(lbs[s], las[b]); vol0[s, b] = max(vol[s], vol[b]); upd_sell[s, b] = (s == v)
                    lim_s[s, b] = lb[s]; lim_b[s, b] = la[b]; bas0[s, b] = bas
    tend = t[t.shape[0] - 1]
    for s in range(n_leg):
        for b in range(n_leg):
            if is_open[s, b] and k < cap:
                o_t0[k] = t0[s, b]; o_t1[k] = tend; o_s[k] = s; o_b[k] = b; o_e0[k] = e0[s, b]; o_emax[k] = emax[s, b]
                o_ages[k] = ages[s, b]; o_ageb[k] = ageb[s, b]; o_sprs[k] = sprs[s, b]; o_sprb[k] = sprb[s, b]
                o_sz[k] = sz0[s, b]; o_vol[k] = vol0[s, b]; o_cens[k] = True; o_upd[k] = upd_sell[s, b]
                o_lims[k] = lim_s[s, b]; o_limb[k] = lim_b[s, b]; o_bas[k] = bas0[s, b]
                k += 1
    return (o_t0[:k], o_t1[:k], o_s[:k], o_b[:k], o_e0[:k], o_emax[:k], o_ages[:k], o_ageb[:k], o_sprs[:k], o_sprb[:k],
            o_sz[:k], o_vol[:k], o_cens[:k], o_upd[:k], o_lims[:k], o_limb[:k], o_bas[:k])


def detect(stream: pl.DataFrame, legs: list[str], clock: str, theta_bps: float = 1.0, basis_tau_s: float = 60.0,
           warmup_s: float = 120.0, max_age_s: float = 30.0, cap: int = 3_000_000) -> pl.DataFrame:
    """stream: QuoteFrame rows plus a `leg` column; `clock` names the observer clock column."""
    idx = {l: i for i, l in enumerate(legs)}
    s = stream.filter(pl.col("leg").is_in(legs)).sort(clock, maintain_order=True)
    leg_i = s["leg"].replace_strict(idx, return_dtype=pl.Int32).to_numpy()
    r = _detect(s[clock].to_numpy(), leg_i, s["bid_px"].to_numpy(), s["ask_px"].to_numpy(), s["bid_sz"].to_numpy(),
                s["ask_sz"].to_numpy(), len(legs), float(theta_bps), basis_tau_s * 1e6, warmup_s * 1e6, max_age_s * 1e6, cap)
    names = ["t_start_us", "t_end_us", "s", "b", "edge0_bps", "edge_max_bps", "age_sell_us", "age_buy_us", "spread_sell_bps",
             "spread_buy_bps", "size", "vol_1s_bps", "censored", "updater_is_sell", "limit_sell_px", "limit_buy_px", "basis0_bps"]
    df = pl.DataFrame(dict(zip(names, r)))
    leg_names = pl.Series("legs", legs)
    df = df.with_columns(
        (pl.col("t_end_us") - pl.col("t_start_us")).alias("duration_us"),
        pl.col("s").map_elements(lambda i: legs[i], return_dtype=pl.Utf8).alias("sell_venue"),
        pl.col("b").map_elements(lambda i: legs[i], return_dtype=pl.Utf8).alias("buy_venue"),
        pl.lit(0.0).alias("net0_bps"),
    ).sort("t_start_us")
    del leg_names
    return df.with_columns(pl.int_range(pl.len(), dtype=pl.Int64).alias("opp_id"))


def opportunity_contract_view(df: pl.DataFrame) -> pl.DataFrame:
    return df.select(list(OPPORTUNITY_FRAME)).cast(OPPORTUNITY_FRAME)
