"""C2 — Scenario generator: non-stationary spatio-temporal demand with ground-truth change labels.

All randomness flows from one integer seed through numpy SeedSequence children, so every policy
evaluated on (scenario, seed) sees the identical request stream (common random numbers).
SYNTHETIC DATA: rates are a parametric model (hotspots x diurnal cycle x shocks/drift/spikes),
not a replay of a real city. See ScenarioConfig for every assumption.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from architecture.contracts.contracts import ChangePoint, DemandTrace


@dataclass(frozen=True)
class ScenarioConfig:
    name: str = "stationary"
    grid: int = 5                      # G x G zones
    horizon: int = 4320                # steps; 1 step = 1 minute -> 3 days
    total_rate: float = 10.0           # mean requests / step over the whole city (before shocks)
    day: int = 1440                    # steps per day
    diurnal_amp: float = 0.35          # total demand = 1 + amp*sin(...)
    hotspots: tuple = ((1.0, 1.0, 1.0, 1.0), (3.0, 3.5, 1.2, 0.7))  # (row, col, sigma, weight)
    floor: float = 0.2                 # uniform share of origin demand
    dest_decay: float = 2.5            # OD distance decay length (zones)
    # abrupt shock: additive surge on an s x s block (a stadium emptying, a failover)
    shock: bool = False
    shock_extra: float = 3.0           # extra rate per shocked zone, in units of (total_rate / Z)
    shock_size: int = 2
    shock_duration: int = 360          # steps (6 h)
    shock_window: tuple = (0.35, 0.55) # onset ~ U(window) * horizon
    # gradual drift: hotspot 0 migrates linearly to drift_to
    drift: bool = False
    drift_to: tuple = (3.5, 0.5)
    drift_window: tuple = (0.1, 0.9)
    # transient spikes (false-alarm bait): short single-zone bursts
    spikes: int = 0
    spike_extra: float = 6.0
    spike_duration: int = 6
    overdispersion: float = 0.0        # 0 -> Poisson; k > 0 -> gamma-Poisson with variance mu + k mu^2


SCENARIOS: dict[str, ScenarioConfig] = {
    "stationary": ScenarioConfig(name="stationary"),
    "shock": ScenarioConfig(name="shock", shock=True),
    "drift": ScenarioConfig(name="drift", drift=True),
    "shock+drift": ScenarioConfig(name="shock+drift", shock=True, drift=True),
    "spikes": ScenarioConfig(name="spikes", spikes=24),
    "shock+drift+spikes": ScenarioConfig(name="shock+drift+spikes", shock=True, drift=True, spikes=24,
                                         overdispersion=0.2),
}


def grid_coords(grid: int) -> np.ndarray:
    rr, cc = np.divmod(np.arange(grid * grid), grid)
    return np.stack([rr, cc], axis=1).astype(float)


def manhattan(grid: int) -> np.ndarray:
    xy = grid_coords(grid)
    return np.abs(xy[:, None, :] - xy[None, :, :]).sum(-1).astype(np.int64)


def _spatial_weights(cfg: ScenarioConfig, centres: np.ndarray) -> np.ndarray:
    """centres: (T, n_hot, 2) -> (T, Z) origin shares summing to 1."""
    xy = grid_coords(cfg.grid)                                   # (Z, 2)
    sig = np.array([h[2] for h in cfg.hotspots])
    wts = np.array([h[3] for h in cfg.hotspots])
    d2 = ((xy[None, None, :, :] - centres[:, :, None, :]) ** 2).sum(-1)   # (T, n_hot, Z)
    bumps = (wts[None, :, None] * np.exp(-d2 / (2 * sig[None, :, None] ** 2))).sum(1)
    bumps /= bumps.sum(1, keepdims=True)
    Z = cfg.grid ** 2
    return cfg.floor / Z + (1 - cfg.floor) * bumps


def od_matrix(cfg: ScenarioConfig) -> np.ndarray:
    """Static P(dest | origin): attraction (hotspots + uniform) x exp(-distance / decay)."""
    centres = np.array([[h[0], h[1]] for h in cfg.hotspots])[None]
    attract = _spatial_weights(replace(cfg, floor=0.5), centres)[0]
    dist = manhattan(cfg.grid)
    p = attract[None, :] * np.exp(-dist / cfg.dest_decay)
    return p / p.sum(1, keepdims=True)


def build_trace(cfg: ScenarioConfig, seed: int) -> DemandTrace:
    T, G = cfg.horizon, cfg.grid
    Z = G * G
    ss = np.random.SeedSequence([seed, 7])
    rng_layout, rng_count, rng_dest = (np.random.default_rng(s) for s in ss.spawn(3))
    t = np.arange(T)

    base_c = np.array([[h[0], h[1]] for h in cfg.hotspots], dtype=float)
    centres = np.repeat(base_c[None], T, axis=0)
    cps: list[ChangePoint] = []
    if cfg.drift:
        t0, t1 = int(cfg.drift_window[0] * T), int(cfg.drift_window[1] * T)
        frac = np.clip((t - t0) / max(1, t1 - t0), 0.0, 1.0)
        centres[:, 0, :] = base_c[0] + frac[:, None] * (np.array(cfg.drift_to) - base_c[0])
        cps += [ChangePoint(t0, "drift_start", tuple(range(Z)), float(np.abs(np.array(cfg.drift_to) - base_c[0]).sum())),
                ChangePoint(t1, "drift_end", tuple(range(Z)), 0.0)]
    weights = _spatial_weights(cfg, centres)                         # (T, Z)
    diurnal = 1.0 + cfg.diurnal_amp * np.sin(2 * np.pi * t / cfg.day - np.pi / 2)
    rates = cfg.total_rate * diurnal[:, None] * weights
    unit = cfg.total_rate / Z

    if cfg.shock:
        s = cfg.shock_size
        r0, c0 = rng_layout.integers(0, G - s + 1, size=2)
        zones = tuple(int((r0 + i) * G + (c0 + j)) for i in range(s) for j in range(s))
        ts = int(rng_layout.uniform(*cfg.shock_window) * T)
        te = min(T, ts + cfg.shock_duration)
        rates[ts:te, list(zones)] += cfg.shock_extra * unit
        cps += [ChangePoint(ts, "shock_on", zones, cfg.shock_extra * unit),
                ChangePoint(te, "shock_off", zones, -cfg.shock_extra * unit)]
    for _ in range(cfg.spikes):
        z = int(rng_layout.integers(0, Z))
        ts = int(rng_layout.integers(0, T - cfg.spike_duration))
        rates[ts:ts + cfg.spike_duration, z] += cfg.spike_extra * unit
        cps += [ChangePoint(ts, "spike_on", (z,), cfg.spike_extra * unit),
                ChangePoint(ts + cfg.spike_duration, "spike_off", (z,), -cfg.spike_extra * unit)]

    if cfg.overdispersion > 0:
        k = cfg.overdispersion
        mu = rng_count.gamma(shape=1.0 / k, scale=rates * k)
        counts = rng_count.poisson(mu)
    else:
        counts = rng_count.poisson(rates)
    counts = counts.astype(np.int32)

    od = od_matrix(cfg)
    flat = counts.reshape(-1)
    offsets = (np.cumsum(flat) - flat).reshape(T, Z).astype(np.int64)
    origin = np.repeat(np.tile(np.arange(Z), T), flat)
    cdf = np.cumsum(od, axis=1)
    cdf[:, -1] = 1.0
    u = rng_dest.random(origin.size)
    dest = np.empty(origin.size, dtype=np.int16)
    for z in range(Z):                      # inverse-CDF sampling per origin zone
        m = origin == z
        dest[m] = np.searchsorted(cdf[z], u[m], side="right")
    cps.sort(key=lambda c: c.t)
    return DemandTrace(rates=rates, counts=counts, req_dest=dest, offsets=offsets, od_prob=od,
                       change_points=cps, name=cfg.name)


def diurnal_profile(cfg: ScenarioConfig, n_days: int = 7, seed: int = 10_000, bin_steps: int = 30) -> np.ndarray:
    """Time-of-day multiplier (mean 1) LEARNED from a separate stationary training trace (no oracle access)."""
    hist_cfg = replace(SCENARIOS["stationary"], grid=cfg.grid, total_rate=cfg.total_rate, day=cfg.day,
                       diurnal_amp=cfg.diurnal_amp, hotspots=cfg.hotspots, floor=cfg.floor,
                       horizon=n_days * cfg.day)
    tr = build_trace(hist_cfg, seed)
    tot = tr.counts.sum(1).astype(float)
    tod_bin = (np.arange(tr.horizon) % cfg.day) // bin_steps
    nb = cfg.day // bin_steps
    prof_bins = np.bincount(tod_bin, weights=tot, minlength=nb) / np.bincount(tod_bin, minlength=nb)
    prof_bins = prof_bins / prof_bins.mean()
    return np.repeat(prof_bins, bin_steps)[: cfg.day]


def historical_shares(cfg: ScenarioConfig, n_days: int = 7, seed: int = 10_000) -> np.ndarray:
    """Average origin shares from the same training history (what a static planner would use)."""
    hist_cfg = replace(SCENARIOS["stationary"], grid=cfg.grid, total_rate=cfg.total_rate, day=cfg.day,
                       diurnal_amp=cfg.diurnal_amp, hotspots=cfg.hotspots, floor=cfg.floor,
                       horizon=n_days * cfg.day)
    tr = build_trace(hist_cfg, seed)
    s = tr.counts.sum(0).astype(float)
    return s / s.sum()
