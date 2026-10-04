"""C4 interceptor (boom) mass balance, one hour, vectorised over (draws, sites).

Invariants (tested): arrived = captured + escaped_entrainment + escaped_overtopping + escaped_bypass;
stored' = stored + captured - refloated - cleared >= 0. Refloated/held-back mass waits in a 'pool'
just upstream and re-arrives on the next ebb (tidal re-floating)."""
from __future__ import annotations

import numpy as np

from ._paths import C


def efficiency(v_ms: np.ndarray, P: dict) -> np.ndarray:
    return P["e_max"] / (1.0 + np.exp((np.abs(v_ms) - P["v50_ms"]) / P["v_width_ms"]))


def access_factor(v_ms, level_m, rain_mm_h, P: dict) -> np.ndarray:
    """Relative clearance rate: 1 at slack/low water; access_poor if current OR level unfavourable;
    access_poor^2 if both; 0 in intense rain."""
    a = np.where(np.abs(v_ms) > P["work_v_ms"], P["access_poor"], 1.0)
    a = a * np.where(level_m > P["work_level_m"], P["access_poor"], 1.0)
    return np.where(rain_mm_h > P["unsafe_rain_mm_h"], 0.0, a)


def bypass_active(q_m3s, level_m, P: dict) -> np.ndarray:
    return (q_m3s > P["q_bypass_m3s"]) | (level_m > P["bypass_level_m"])


def step(stored, pool, fresh_kg, v_ms, level_m, bypass, crew_kg_cap, P: dict) -> dict:
    """One hour. fresh_kg: catchment wash-off arriving from upstream this hour."""
    ebb = v_ms > 0.0
    pool = pool + np.where(ebb, 0.0, fresh_kg)            # flood tide holds arrivals upstream
    ret = np.where(ebb, pool * P["k_return_per_h"], 0.0)
    pool = pool - ret
    arrived = np.where(ebb, fresh_kg + ret, 0.0)
    eff = efficiency(v_ms, P)
    pot = eff * arrived
    room = np.maximum(P["capacity_kg"] - stored, 0.0)
    captured = np.where(bypass, 0.0, np.minimum(pot, room))
    over = np.where(bypass, 0.0, pot - np.minimum(pot, room))
    ent = np.where(bypass, 0.0, arrived - pot)
    byp = np.where(bypass, arrived, 0.0)
    s1 = stored + captured
    k = np.where(bypass, P["k_flood_release"], np.where(v_ms < 0.0, P["k_refloat_per_h"], 0.0))
    refl = k * s1
    s2 = s1 - refl
    cleared = np.minimum(s2, crew_kg_cap)
    return dict(stored=s2 - cleared, pool=pool + refl, arrived=arrived, captured=captured, ent=ent,
                over=over, byp=byp, refl=refl, cleared=cleared)


def interceptor_series(site_id, t, rec: dict, capacity_kg: float, source: str) -> "C.InterceptorSeries":
    r = lambda a: np.round(np.asarray(a, float), 3).tolist()  # noqa: E731
    return C.InterceptorSeries(
        site_id=site_id, t=list(t), arrived_kg=r(rec["arrived"]), captured_kg=r(rec["captured"]),
        escaped_entrainment_kg=r(rec["ent"]), escaped_overtopping_kg=r(rec["over"]),
        escaped_bypass_kg=r(rec["byp"]), refloated_kg=r(rec["refl"]), cleared_kg=r(rec["cleared"]),
        stored_kg=r(rec["stored"]), fill_fraction=r(np.asarray(rec["stored"]) / capacity_kg),
        provenance=C.Provenance(kind="simulated", source=source,
                                notes="SIMULATED digital twin (nominal parameters); not field data"))
