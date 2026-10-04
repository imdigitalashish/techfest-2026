"""C9 risk forecaster. Runs the twin's NOMINAL-parameter model forward from the state implied by
past (observed) rain, driven by the archived day-ahead NWP rain forecast (JMA GSM via Open-Meteo,
issued >= 1 day before) and the harmonic tide prediction. Issued daily at 00 UTC (05:30 IST)."""
from __future__ import annotations

import numpy as np

from . import hydraulics as HY
from . import interceptor as IC
from . import params as PR
from ._paths import C

_CACHE: dict = {}
SRC = "component:twin_sim.risk_forecaster (nominal-parameter twin + JMA GSM day-ahead rain + harmonic tide)"


def _sig(x):
    return 1.0 / (1.0 + np.exp(-x))


def season_forecast(year: int) -> dict:
    if year in _CACHE:
        return _CACHE[year]
    from .sim import param_arrays, physics
    Pn = param_arrays([PR.nominal()])
    ph = physics(year, Pn)                     # observed-rain state trajectory (what gauges tell us)
    p1 = {k: (v[0] if isinstance(v, np.ndarray) and v.ndim == 2 else v) for k, v in Pn.items()}
    T, S = ph["fresh"].shape[0], ph["fresh"].shape[2]
    fcr, tide = ph["fc"], ph["tide"]
    dtide = np.gradient(tide, axis=0)
    alpha, qb = HY.reservoir_alpha(p1), HY.base_flow_m3s(p1)
    nd = T // 24
    out = {k: np.zeros((nd, S)) for k in ("arr24", "arr48", "R24", "R48", "p_bypass", "e_cap", "max_tide")}
    out["access"] = np.zeros((nd, 24, S))
    for d in range(nd):
        t0 = d * 24
        M = ph["stock"][t0, 0]
        q = ph["q"][t0 - 1, 0] if t0 > 0 else qb
        # Causality: precipitation_previous_day1 for hours t0..t0+23 comes from runs issued on the previous
        # day (before the 00 UTC decision); for t0+24.. it would come from runs issued after t0 -> not used.
        hz = min(24, T - t0)
        r = fcr[t0:t0 + hz]
        qs = np.empty((hz, S))
        for i in range(hz):
            q = HY.runoff_step(q, r[i], p1, alpha, qb)
            qs[i] = q
        lev, v = HY.flow_state(qs, tide[t0:t0 + hz], dtide[t0:t0 + hz], p1)
        R24 = r[:24].sum(0)
        R48 = R24                                   # 24 h causal horizon (see above); kept for API stability
        out["R24"][d], out["R48"][d] = R24, R48
        kd = p1["k_dry_per_h"]
        out["arr24"][d] = M * (1 - np.exp(-p1["kw_per_mm"] * R24)) + kd * M * 24
        out["arr48"][d] = out["arr24"][d]
        zq = (qs.max(0) / p1["q_bypass_m3s"] - 1) / 0.15
        zl = (lev.max(0) - p1["bypass_level_m"]) / 0.1
        out["p_bypass"][d] = 1 - (1 - _sig(zq)) * (1 - _sig(zl))
        eff = IC.efficiency(v[:24], p1)
        ebb = v[:24] > 0
        out["e_cap"][d] = np.where(ebb.any(0), (eff * ebb).sum(0) / np.maximum(ebb.sum(0), 1), p1["e_max"])
        out["max_tide"][d] = tide[t0:t0 + 24].max(0)
        a = IC.access_factor(v[:24], lev[:24], r[:24], p1)
        out["access"][d, : a.shape[0]] = a
    # Ablation input (P2_nofc): predicted access from the harmonic tide and dry-weather base flow only, no rain forecast
    lev_t, v_t = HY.flow_state(np.broadcast_to(qb, tide.shape), tide, dtide, p1)
    acc_t = IC.access_factor(v_t, lev_t, np.zeros_like(tide), p1)
    out["access_tide"] = acc_t[: nd * 24].reshape(nd, 24, S)
    out["capacity_kg"] = p1["capacity_kg"]
    out["clear_rate"] = float(p1["clear_rate_kg_h"][0])
    out["t"] = ph["t"]
    out["_state"] = {"stock": ph["stock"][:, 0], "q": ph["q"][:, 0], "tide": tide, "fcr": fcr, "p1": p1}
    _CACHE[year] = out
    return out


def p_overflow(fc: dict, d: int, fill_obs: np.ndarray) -> np.ndarray:
    """P(barrier overtops or must release within 24 h) from sensed fill + forecast arrivals."""
    cap = fc["capacity_kg"]
    exp_fill = (fill_obs * cap + fc["e_cap"][d] * fc["arr24"][d]) / cap
    p_top = _sig((exp_fill - 1.0) / 0.15)
    return 1 - (1 - p_top) * (1 - fc["p_bypass"][d]), exp_fill


def site_forecasts(fc: dict, d: int, fill_obs: np.ndarray, site_ids: list) -> list:
    p, ef = p_overflow(fc, d, fill_obs)
    t0 = fc["t"][d * 24].to_pydatetime()
    return [C.SiteForecast(
        site_id=sid, issued_at=t0, horizon_h=24, p_overflow=float(np.clip(p[i], 0, 1)),
        expected_arrival_kg=float(round(fc["arr24"][d, i], 1)), expected_fill_fraction=float(round(max(ef[i], 0), 3)),
        drivers={"rain_mm_next_24h_fc": float(round(fc["R24"][d, i], 1)),
                 "max_tide_m_next_24h": float(round(fc["max_tide"][d, i], 2)),
                 "p_bypass_24h": float(round(fc["p_bypass"][d, i], 3)),
                 "sensed_fill": float(round(fill_obs[i], 3))},
        provenance=C.Provenance(kind="model_output", source=SRC,
                                notes="inputs: archived real NWP forecast + SIMULATED fill sensor"))
        for i, sid in enumerate(site_ids)]


def horizon_forecasts(fc: dict, d: int, fill_obs: np.ndarray, site_ids: list, horizon: int,
                      fc2: np.ndarray | None = None) -> list:
    """Dashboard export (policies are unaffected). horizon 24: the policy forecaster above. horizon 48: hours 0-23
    use precipitation_previous_day1 and hours 24-47 use precipitation_previous_day2 (predicted 48 h before valid
    time), so every input was issued before 00 UTC of day d."""
    if horizon == 24:
        return site_forecasts(fc, d, fill_obs, site_ids)
    st = fc["_state"]
    p1, tide = st["p1"], st["tide"]
    dtide = np.gradient(tide, axis=0)
    alpha, qb = HY.reservoir_alpha(p1), HY.base_flow_m3s(p1)
    t0, T = d * 24, tide.shape[0]
    hz = min(horizon, T - t0)
    r = np.concatenate([st["fcr"][t0:t0 + 24], fc2[t0 + 24:t0 + hz]])[:hz]
    M = st["stock"][t0]
    q = st["q"][t0 - 1] if t0 > 0 else qb
    qs = np.empty((hz, r.shape[1]))
    for i in range(hz):
        q = HY.runoff_step(q, r[i], p1, alpha, qb)
        qs[i] = q
    lev, v = HY.flow_state(qs, tide[t0:t0 + hz], dtide[t0:t0 + hz], p1)
    R = r.sum(0)
    arr = M * (1 - np.exp(-p1["kw_per_mm"] * R)) + p1["k_dry_per_h"] * M * hz
    zq = (qs.max(0) / p1["q_bypass_m3s"] - 1) / 0.15
    zl = (lev.max(0) - p1["bypass_level_m"]) / 0.1
    p_byp = 1 - (1 - _sig(zq)) * (1 - _sig(zl))
    eff, ebb = IC.efficiency(v, p1), v > 0
    e_cap = np.where(ebb.any(0), (eff * ebb).sum(0) / np.maximum(ebb.sum(0), 1), p1["e_max"])
    cap = fc["capacity_kg"]
    ef = (fill_obs * cap + e_cap * arr) / cap
    p = 1 - (1 - _sig((ef - 1.0) / 0.15)) * (1 - p_byp)
    t0d = fc["t"][t0].to_pydatetime()
    return [C.SiteForecast(
        site_id=sid, issued_at=t0d, horizon_h=horizon, p_overflow=float(np.clip(p[i], 0, 1)),
        expected_arrival_kg=float(round(arr[i], 1)), expected_fill_fraction=float(round(max(ef[i], 0), 3)),
        drivers={"rain_mm_next_24h_fc": float(round(r[:24, i].sum(), 1)),
                 "rain_mm_next_48h_fc": float(round(R[i], 1)),
                 "max_tide_m_next_48h": float(round(tide[t0:t0 + hz, i].max(), 2)),
                 "p_bypass_48h": float(round(p_byp[i], 3)), "sensed_fill": float(round(fill_obs[i], 3))},
        provenance=C.Provenance(kind="model_output", source=SRC,
                                notes="48 h: day-1 + day-2 archived JMA GSM forecasts (both issued before 00 UTC); "
                                      "dashboard export only, not used by the P2 policy"))
        for i, sid in enumerate(site_ids)]

