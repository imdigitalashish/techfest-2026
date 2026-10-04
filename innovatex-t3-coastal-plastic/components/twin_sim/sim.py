"""Season simulator: hourly, vectorised over Monte Carlo draws (D) x sites (S).

Truth = each draw's parameters + real forcing. Policies see only what a real operator could:
noisy SIMULATED fill sensors, the harmonic tide prediction, and the archived day-ahead NWP rain
forecast via risk_forecaster (nominal parameters, never the draw's true ones)."""
from __future__ import annotations

import numpy as np

from . import catchment_load as CL
from . import forcing as FO
from . import hydraulics as HY
from . import interceptor as IC
from . import params as PR
from .sites import get_sites

TUNE_YEARS = [2019, 2020, 2021, 2022, 2023]
HOLDOUT_YEARS = [2024, 2025]


def param_arrays(draws: list[dict]) -> dict:
    sites = get_sites()
    D, S = len(draws), len(sites)
    P = {k: np.array([[d[k]] * S for d in draws], float) for k in draws[0]}
    col = lambda vals: np.broadcast_to(np.asarray(vals, float), (D, S)).copy()  # noqa: E731
    P["area_km2"] = col([s.catchment.area_km2 for s in sites])
    P["population"] = col([s.catchment.population for s in sites])
    P["width_m"] = col([s.channel_width_m for s in sites])
    P["tidal_store_m2"] = col([PR.TIDAL_STORE_KM2[s.site_id] * 1e6 for s in sites]) * P["tidal_store_mult"]
    P["capacity_kg"] = col([s.boom_capacity_m3 for s in sites]) * P["bulk_density_kg_m3"]
    P["q_bypass_m3s"] = (P["runoff_coeff"] * P["bypass_rain_mm_h"] * P["area_km2"] / 3.6
                         + HY.base_flow_m3s(P))
    return P


def physics(year: int, P: dict, rain_key: str = "rain") -> dict:
    """Policy-independent part: wash-off load, routed discharge, level, velocity, bypass, access."""
    s = FO.season(year)
    rain = s.rain if rain_key == "rain" else s.fc_rain
    T = len(s.t)
    D, S = P["area_km2"].shape
    gen = CL.generation_kg_h(P)
    stock = CL.initial_stock_kg(P)
    alpha, qb = HY.reservoir_alpha(P), HY.base_flow_m3s(P)
    q = qb.copy()
    fresh = np.empty((T, D, S))
    Q = np.empty((T, D, S))
    M = np.empty((T, D, S))
    for t in range(T):
        M[t] = stock
        stock, w = CL.washoff_step(stock, rain[t], P, gen)
        q = HY.runoff_step(q, rain[t], P, alpha, qb)
        fresh[t], Q[t] = w, q
    dtide = np.gradient(s.tide, axis=0)
    level, v = HY.flow_state(Q, s.tide[:, None, :], dtide[:, None, :], P)
    return dict(year=year, t=s.t, rain=rain, tide=s.tide, fc=s.fc_rain, fresh=fresh, q=Q, stock=M,
                level=level, v=v, bypass=IC.bypass_active(Q, level, P),
                access=IC.access_factor(v, level, rain[:, None, :], P))


def run_season(phys: dict, P: dict, policy, fc: dict, sensor_seed: int, record: bool = False) -> dict:
    """policy(day_ctx) -> list[(site_idx, start_hour_utc, hours)] per draw (see dispatch.py)."""
    from .dispatch import DayCtx, crew_matrix
    T, D, S = phys["fresh"].shape
    rng = np.random.default_rng(sensor_seed)
    stored = np.zeros((D, S))
    pool = np.zeros((D, S))
    keys = ["arrived", "captured", "ent", "over", "byp", "refl", "rel", "cleared"]
    tot = {k: np.zeros((D, S)) for k in keys}
    over_h = np.zeros((D, S))
    crew_h = np.zeros(D)
    rec = {k: [] for k in keys + ["stored", "fill_obs"]} if record else None
    plans = []
    for d in range(T // 24):
        t0 = d * 24
        fill_obs = np.clip(stored / P["capacity_kg"] + rng.normal(0, 1, (D, S)) * P["fill_noise_sd"], 0, 1)
        ctx = DayCtx(day=d, t0=t0, fill_obs=fill_obs, fc=fc, S=S)
        assign = policy(ctx)                       # list (len D) of lists of (s, start, hours)
        W = crew_matrix(assign, D, S)              # (D, S, 24) crews working per UTC hour
        crew_h += W.sum(axis=(1, 2))
        if record:
            plans.append(assign)
        for h in range(24):
            t = t0 + h
            cap_h = W[:, :, h] * P["clear_rate_kg_h"] * phys["access"][t]
            r = IC.step(stored, pool, phys["fresh"][t], phys["v"][t], phys["level"][t], phys["bypass"][t],
                        cap_h, P)
            stored, pool = r["stored"], r["pool"]
            for k in keys:
                tot[k] += r[k]
            over_h += r["over"] > 1e-9
            if record:
                for k in keys:
                    rec[k].append(r[k])
                rec["stored"].append(stored)
                rec["fill_obs"].append(fill_obs)
    escaped = tot["ent"] + tot["over"] + tot["byp"]
    out = dict(escaped=escaped, load=phys["fresh"].sum(axis=0), overflow_h=over_h,
               bypass_h=phys["bypass"].sum(axis=0), crew_h=crew_h, end_stored=stored, end_pool=pool, **tot)
    if record:
        out["rec"] = {k: np.array(v) for k, v in rec.items()}
        out["plans"] = plans
    return out


def evaluate(policy_name: str, years: list[int], n_draws: int, seed: int = 20261004, knobs: dict | None = None,
             draws: list[dict] | None = None) -> dict:
    """Sum over `years` of per-draw totals (D,) for a policy. Fixed seeds -> deterministic."""
    from . import dispatch as DP
    from . import risk_forecaster as RF
    draws = draws or PR.draw(n_draws, seed)
    P = param_arrays(draws)
    agg = None
    for y in years:
        phys = physics(y, P)
        fc = RF.season_forecast(y)
        res = run_season(phys, P, DP.make_policy(policy_name, fc, knobs), fc, sensor_seed=seed + y)
        part = {k: res[k].sum(axis=-1) if res[k].ndim == 2 else res[k]
                for k in ("escaped", "load", "overflow_h", "bypass_h", "crew_h", "cleared", "captured")}
        agg = part if agg is None else {k: agg[k] + part[k] for k in agg}
    return agg
