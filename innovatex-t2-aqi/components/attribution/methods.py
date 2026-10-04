"""C6 attribution methods: the ONLY file the autoresearch loop may edit.

Each method gets the per-hour ring data and returns (increment_estimate µg/m³, abstain: bool) arrays.
Inputs (pandas DataFrame `obs`, hourly, index = IST timestamps):
  raw_N, raw_E, raw_S, raw_W   raw sensor PM10 per node (µg/m³, uncalibrated, SIMULATED sensors on REAL background)
  rh                            relative humidity % (ERA5, real)
  ws_meas, wd_meas              site wind vane: speed m/s, direction FROM in degrees (real ERA5 + simulated vane error)
`geom`: dict node -> (x_east_m, y_north_m) relative to the site centre.
Methods must be causal: at hour t they may use only rows <= t.
"""
import numpy as np
import pandas as pd

NODES = ["N", "E", "S", "W"]
CANDIDATE = "ring_selfcal"  # the method the frozen evaluator scores as the headline scalar


def _travel_unit(wd_from_deg):
    to = np.deg2rad((np.asarray(wd_from_deg) + 180.0) % 360.0)
    return np.sin(to), np.cos(to)  # (east, north) components of the direction the air travels


def pair_fixed(obs, geom):
    """Baseline: fixed upwind (W) and downwind (E) nodes, raw readings, no abstention."""
    return (obs["raw_E"] - obs["raw_W"]).values, np.zeros(len(obs), bool)


def _ring(vals, obs, geom, calm_ms=0.5):
    ue, un = _travel_unit(obs["wd_meas"].values)
    proj = np.stack([geom[n][0] * ue + geom[n][1] * un for n in NODES], axis=1)  # along-wind position of each node
    V = np.stack([vals[n] for n in NODES], axis=1)
    rows = np.arange(len(obs))
    down, up = proj.argmax(1), proj.argmin(1)
    inc = V[rows, down] - V[rows, up]
    abstain = obs["ws_meas"].values < calm_ms
    return inc, abstain


def ring(obs, geom):
    """Wind-resolved ring: downwind-most minus upwind-most node, raw readings; abstain in calm."""
    return _ring({n: obs[f"raw_{n}"].values for n in NODES}, obs, geom)


def ring_selfcal(obs, geom, window_days=14, idle_hours=(0, 1, 2, 3, 4, 5)):
    """Ring + inter-node self-calibration: during idle night hours every node sees the same background, so fit each
    node to the ring median (ratio of medians) over a trailing window and rescale. Causal: uses only past idle hours."""
    raw = pd.DataFrame({n: obs[f"raw_{n}"] for n in NODES})
    med = raw.median(axis=1).clip(lower=1.0)
    idle = raw.index.hour.isin(idle_hours)
    cal = {}
    for n in NODES:
        ratio = (raw[n] / med).where(idle)
        # trailing median ratio over past idle hours (shifted by one row so hour t never uses itself)
        r = ratio.rolling(f"{window_days}D", min_periods=24).median().shift(1).ffill().fillna(1.0).clip(0.2, 5.0)
        cal[n] = (raw[n] / r).values
    return _ring(cal, obs, geom)


def ring_refcal(obs, geom):
    """Fair baseline (review 08:35): ring co-calibrated by weekly reference visits. Each node is divided by its gain to
    ambient air measured at the latest past visit (`refvisit_<node>`, NaN between visits; evaluator v2 only)."""
    cal = {}
    for n in NODES:
        col = f"refvisit_{n}"
        g = obs[col].shift(1).ffill().fillna(1.0).clip(0.2, 5.0) if col in obs else pd.Series(1.0, index=obs.index)
        cal[n] = (obs[f"raw_{n}"] / g).values
    return _ring(cal, obs, geom)


def ring_refcal14(obs, geom):
    """Stronger reference baseline (gpt-6-sol review, 4 Oct): causal 14-day median of past weekly reference-visit gains."""
    cal = {}
    for n in NODES:
        col = f"refvisit_{n}"
        if col in obs:
            g = obs[col].shift(1).rolling("14D", min_periods=1).median().ffill().fillna(1.0).clip(0.2, 5.0)
        else:
            g = pd.Series(1.0, index=obs.index)
        cal[n] = (obs[f"raw_{n}"] / g).values
    return _ring(cal, obs, geom)


METHODS = {"pair_fixed": pair_fixed, "ring": ring, "ring_selfcal": ring_selfcal, "ring_refcal": ring_refcal, "ring_refcal14": ring_refcal14}
