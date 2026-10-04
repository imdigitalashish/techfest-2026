"""C3 outfall hydraulics: rational-method runoff routed through a linear reservoir, plus tide.
Water level = tide + a*Q^0.6; signed surface velocity (+ seaward) = (Q_river - A_tidal * d(tide)/dt) / section."""
from __future__ import annotations

import numpy as np

from ._paths import C


def reservoir_alpha(P: dict) -> np.ndarray:
    k_h = (1.5 + 0.05 * P["area_km2"]) * P["k_res_mult"]
    return 1.0 - np.exp(-1.0 / k_h)


def base_flow_m3s(P: dict) -> np.ndarray:
    return P["population"] * P["sewage_l_cap_day"] / 1000.0 / 86400.0


def runoff_step(q: np.ndarray, rain_mm_h: np.ndarray, P: dict, alpha: np.ndarray, qbase: np.ndarray):
    q_in = P["runoff_coeff"] * rain_mm_h * P["area_km2"] / 3.6 + qbase
    return q + (q_in - q) * alpha


def flow_state(q: np.ndarray, tide_m: np.ndarray, dtide_m_h: np.ndarray, P: dict):
    """Returns (water_level_m MSL, surface_velocity_ms signed + seaward)."""
    level = tide_m + P["stage_coeff"] * np.power(np.maximum(q, 0.0), 0.6)
    depth = np.maximum(P["depth_msl_m"] + level, 0.5)
    q_tide = -P["tidal_store_m2"] * dtide_m_h / 3600.0      # rising tide -> landward (negative)
    v = (q + q_tide) / (P["width_m"] * depth)
    return level, v


def hydraulic_series(site_id, t, q, v, level, source: str) -> "C.HydraulicSeries":
    r = lambda a: np.round(np.asarray(a, float), 3).tolist()  # noqa: E731
    return C.HydraulicSeries(site_id=site_id, t=list(t), discharge_m3s=r(q), surface_velocity_ms=r(v),
                             water_level_m=r(level),
                             provenance=C.Provenance(kind="simulated", source=source,
                                                     notes="SIMULATED from real rain + harmonic tide; ASSUMPTION geometry"))
