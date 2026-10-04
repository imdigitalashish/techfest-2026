"""Parameter table for the twin. Every entry: nominal value, Monte Carlo range, unit, source/ASSUMPTION.
research/components/twin.md renders this table (python -m twin_sim.params --md)."""
from __future__ import annotations

import numpy as np

BRIEF = "_briefs/innovatex.txt line 121 (official InnovateX statement): ~5 million kg/yr from Mumbai waterways"

# name: (nominal, low, high, unit, kind, reasoning/source)   kind in {source, assumption}
PARAMS = {
    # ---- C2 catchment load
    "city_load_t_yr": (5000, 5000, 5000, "t/yr", "source", BRIEF),
    "city_area_km2": (603, 603, 603, "km2", "assumption",
                      "Greater Mumbai area, commonly quoted; UNVERIFIED in this run. Used only to scale load per km2"),
    "load_mult": (1.0, 0.3, 1.5, "-", "assumption",
                  "share of the city-wide flux that is floating macroplastic reaching these outfalls; wide range"),
    "stock0_days": (30, 10, 60, "days of generation", "assumption",
                    "catchment stock on 1 Jun after dry-season build-up minus pre-monsoon desilting"),
    "kw_per_mm": (0.08, 0.03, 0.20, "1/mm", "assumption",
                  "exponential wash-off M*(1-exp(-k*rain)) as in SWMM-style build-up/wash-off; 25 mm washes ~86% at nominal"),
    "k_dry_per_h": (0.002, 0.0005, 0.005, "1/h", "assumption", "dry-weather (sewage base flow) transport of floatables"),
    "kg_per_item": (0.01, 0.005, 0.02, "kg/item", "assumption", "mean mass of a floating macroplastic item"),
    # ---- C3 hydraulics
    "runoff_coeff": (0.7, 0.5, 0.9, "-", "assumption", "rational-method C for dense urban catchments"),
    "k_res_mult": (1.0, 0.5, 2.0, "-", "assumption", "linear-reservoir lag k = (1.5 h + 0.05 h/km2 * area) * mult"),
    "sewage_l_cap_day": (150, 100, 200, "L/person/day", "assumption", "dry-weather flow in nullahs (untreated sewage)"),
    "depth_msl_m": (2.5, 1.5, 4.0, "m", "assumption", "channel depth below MSL at the boom line"),
    "stage_coeff": (0.05, 0.02, 0.10, "m/(m3/s)^0.6", "assumption", "river-flow stage rise a*Q^0.6 on top of tide"),
    "tidal_store_mult": (1.0, 0.5, 2.0, "-", "assumption",
                         "upstream tidal storage area (site table) multiplier; sets tidal current = A*deta/dt / section"),
    # ---- C4 interceptor
    "e_max": (0.85, 0.70, 0.95, "-", "assumption", "capture of floating items at slack water (misses submerged items)"),
    "v50_ms": (0.45, 0.30, 0.70, "m/s", "assumption",
               "speed at which boom capture halves through entrainment under the skirt; oil-boom practice ~0.35-0.5 m/s"
               " normal velocity (UNVERIFIED here), diagonal booms tolerate more"),
    "v_width_ms": (0.08, 0.05, 0.12, "m/s", "assumption", "logistic width of the entrainment curve"),
    "bulk_density_kg_m3": (150, 80, 300, "kg/m3", "assumption", "wet mixed floating debris retained at a boom"),
    "k_refloat_per_h": (0.03, 0.01, 0.08, "1/h", "assumption", "stored debris re-floated per flood-tide hour (flow reversal)"),
    "k_return_per_h": (0.30, 0.15, 0.50, "1/h", "assumption", "held-back/refloated debris returning to the boom per ebb hour"),
    "bypass_rain_mm_h": (12, 8, 20, "mm/h equiv. (ERA5 scale)", "assumption",
                         "boom opened/bypassed (flood release) when routed runoff exceeds this rain-equivalent"),
    "bypass_level_m": (2.6, 2.3, 3.2, "m MSL", "assumption", "boom bypass/overtopping when water level exceeds this"),
    "k_flood_release": (0.3, 0.1, 0.6, "1/h", "assumption", "stored mass released per bypass hour"),
    # ---- C10 crews / clearance
    "n_crews": (2, 2, 2, "crews", "assumption", "fixed budget: 2 crews x 8 h/day for every policy (equal crew-hours)"),
    "shift_h": (8, 8, 8, "h", "assumption", "one shift per crew per day"),
    "clear_rate_kg_h": (400, 200, 800, "kg/h", "assumption", "crew with nets/grab at good access (low water, slack)"),
    "work_v_ms": (0.5, 0.3, 0.8, "m/s", "assumption", "above this current, boat work at the boom is slowed"),
    "work_level_m": (0.5, 0.0, 1.0, "m MSL", "assumption", "above this level, debris is out of reach from the bank"),
    "access_poor": (0.3, 0.15, 0.5, "-", "assumption", "relative clearance rate when current OR level is unfavourable"),
    "unsafe_rain_mm_h": (15, 10, 25, "mm/h", "assumption", "no work in intense rain"),
    # ---- C7/C8 simulated sensors
    "fill_noise_sd": (0.05, 0.02, 0.10, "fraction", "assumption", "SIMULATED fill sensor error (camera/range sensor)"),
}

FIXED = {k for k, v in PARAMS.items() if v[1] == v[2]}

# Per-site upstream tidal storage area (km2), ASSUMPTION (mangrove/mudflat area behind each boom line).
TIDAL_STORE_KM2 = {"mithi_mahim": 0.5, "oshiwara_malad": 0.3, "dahisar_mouth": 0.25, "trombay_mahul": 0.05}


def nominal() -> dict:
    return {k: v[0] for k, v in PARAMS.items()}


def draw(n: int, seed: int = 20261004) -> list[dict]:
    """Latin-hypercube-free simple Monte Carlo: independent uniform draws over each ASSUMPTION range."""
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        p = {}
        for k, (nom, lo, hi, *_r) in PARAMS.items():
            p[k] = nom if lo == hi else float(rng.uniform(lo, hi))
        out.append(p)
    return out


def markdown_table() -> str:
    rows = ["| parameter | nominal | MC range | unit | kind | source / reasoning |", "|---|---|---|---|---|---|"]
    for k, (nom, lo, hi, unit, kind, why) in PARAMS.items():
        rng = "fixed" if lo == hi else f"{lo} – {hi}"
        rows.append(f"| `{k}` | {nom} | {rng} | {unit} | {kind.upper() if kind == 'assumption' else kind} | {why} |")
    return "\n".join(rows)


if __name__ == "__main__":
    print(markdown_table())
