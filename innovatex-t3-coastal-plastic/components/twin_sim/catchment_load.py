"""C2 catchment plastic load: dry-weather build-up + exponential rain wash-off (first flush).
All parameters are ASSUMPTIONS from params.py, drawn over ranges in the Monte Carlo."""
from __future__ import annotations

import numpy as np

from ._paths import C


def generation_kg_h(P: dict) -> np.ndarray:
    """Plastic reaching the drains per hour: city-wide flux (brief) per km2 x catchment area x multiplier."""
    return P["city_load_t_yr"] * 1000.0 / P["city_area_km2"] / 8760.0 * P["load_mult"] * P["area_km2"]


def initial_stock_kg(P: dict) -> np.ndarray:
    return generation_kg_h(P) * 24.0 * P["stock0_days"]


def washoff_step(stock: np.ndarray, rain_mm_h: np.ndarray, P: dict, gen: np.ndarray):
    """One hour: wash-off W = M(1-exp(-k_w r)) + k_dry M; then M += build-up - W. Returns (M_new, W)."""
    w = stock * (1.0 - np.exp(-P["kw_per_mm"] * rain_mm_h)) + stock * P["k_dry_per_h"]
    return stock + gen - w, w


def load_series(site_id: str, t, kg_per_h, kg_per_item: float, simulated_source: str) -> "C.LoadSeries":
    kg = np.round(np.asarray(kg_per_h, float), 3)
    return C.LoadSeries(site_id=site_id, t=list(t), kg_per_h=kg.tolist(),
                        items_per_h=np.round(kg / kg_per_item, 1).tolist(),
                        provenance=C.Provenance(kind="simulated", source=simulated_source,
                                                notes="SIMULATED: build-up/wash-off with ASSUMPTION parameters"))
