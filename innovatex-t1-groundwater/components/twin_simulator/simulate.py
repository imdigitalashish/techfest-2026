"""C0 twin-simulator — truth-labelled RWH recharge-pit stage series driven by REAL Delhi rainfall.

Everything this module outputs is SIMULATED (provenance=simulated). Only the rain driver is real:
ERA5 hourly precipitation for central Delhi via Open-Meteo (components/data-ingest/fetch_delhi.py).

Physics (linear-reservoir pit, 1-minute step):
    inflow        q_in = runoff_coeff * catchment_m2 * rain_rate          (0 once the inlet is blocked)
    storage       V = A*h ; loss over one minute = V*(1-exp(-k/60)) (k = recession constant, 1/h)
    overflow      anything above overflow_stage*A spills
    clogging      k = k0 * exp(-clog_rate * cumulative_inflow_m3)
Faults injected: blocked inlet, progressive clogging, bucket "fakes" (water poured with no rain),
sensor noise (sigma 3 mm), sparse dropouts. Hourly ERA5 rain is split into minutes with a seeded
random burst pattern (ERA5 is smooth; real gauges are not). Mass balance closes exactly:
    sum(inflow) = sum(infiltration) + sum(overflow) + final storage
"""
from __future__ import annotations

import pathlib
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[2]
HOURLY = ROOT / ".data" / "delhi_weather_hourly.csv"
# Frozen copy of the exact hourly series used by the evaluators/demo (monsoons 2024 and 2025), committed so
# results are reproducible even if the upstream archive changes. Source: Open-Meteo historical archive, DEFAULT
# model selection (not pinned) — it is NOT identical to pinned ERA5 (checked 4 Oct 2026; see eval/data/README.md).
FIXTURE = ROOT / "eval" / "data" / "delhi_rain_hourly_openmeteo_default_monsoon2024_2025.csv"


@dataclass
class PitTruth:
    structure_id: str
    kind: str
    catchment_m2: float
    runoff_coeff: float
    pit_area_m2: float
    overflow_stage_m: float
    k0_per_h: float
    clog_rate_per_m3: float
    inlet_blocked_from: pd.Timestamp | None
    fakes: list[tuple[pd.Timestamp, float]] = field(default_factory=list)
    drain_exponent: float = 1.0      # 1 = linear reservoir (evaluator v1); 0.5 = orifice-like (evaluator v2)


def load_rain(start: str, end: str) -> pd.Series:
    src = HOURLY if HOURLY.exists() else FIXTURE
    h = pd.read_csv(src, parse_dates=["datetime_ist"]).set_index("datetime_ist")["precip_mm"]
    return h.loc[start:end].fillna(0.0)


def minute_rain(hourly_mm: pd.Series, rng: np.random.Generator) -> pd.Series:
    vals = np.zeros(len(hourly_mm) * 60)
    for i, mm in enumerate(hourly_mm.to_numpy()):
        if mm > 0:
            vals[i * 60:(i + 1) * 60] = mm * rng.dirichlet(np.full(60, 0.3))
    idx = pd.date_range(hourly_mm.index[0], periods=len(vals), freq="1min")
    return pd.Series(vals, index=idx, name="rain_mm")


def make_fleet(n: int, seed: int, start: pd.Timestamp, end: pd.Timestamp) -> list[PitTruth]:
    rng = np.random.default_rng(seed)
    span = (end - start).total_seconds() / 60
    fleet = []
    for i in range(n):
        kind = str(rng.choice(["healthy", "clogging", "blocked", "faker"], p=[0.5, 0.25, 0.1, 0.15]))
        blocked = (start + pd.Timedelta(minutes=float(rng.uniform(0.1, 0.5) * span))) if kind == "blocked" else None
        fakes = []
        if kind == "faker":
            for _ in range(int(rng.integers(1, 4))):
                t = (start + pd.Timedelta(minutes=float(rng.uniform(0.05, 0.95) * span))).floor("min")
                fakes.append((t, float(rng.uniform(0.5, 2.0))))
        fleet.append(PitTruth(
            structure_id=f"SIM-PIT-{seed:03d}-{i:03d}", kind=kind,
            catchment_m2=float(rng.uniform(100, 500)),          # DJB RWH mandate starts at 100 m2 plots
            runoff_coeff=float(rng.uniform(0.6, 0.9)),
            pit_area_m2=float(rng.uniform(1.5, 4.0)),
            overflow_stage_m=float(rng.uniform(1.0, 2.0)),
            k0_per_h=float(rng.uniform(0.15, 0.6)),
            clog_rate_per_m3=float(rng.uniform(0.004, 0.012)) if kind == "clogging" else float(rng.uniform(0, 0.0005)),
            inlet_blocked_from=blocked, fakes=fakes))
    return fleet


def simulate_pit(p: PitTruth, rain_min: pd.Series, rng: np.random.Generator, noise_m: float = 0.003):
    """Return (observed stage DataFrame, per-minute truth DataFrame)."""
    n = len(rain_min)
    idx = rain_min.index
    r = rain_min.to_numpy()
    q_rain = p.runoff_coeff * p.catchment_m2 * r / 1000.0
    if p.inlet_blocked_from is not None:
        q_rain[idx >= p.inlet_blocked_from] = 0.0
    q_fake = np.zeros(n)
    for t, v in p.fakes:
        j = idx.searchsorted(t)
        if j < n:
            q_fake[j] += v
    h = np.zeros(n); infil = np.zeros(n); over = np.zeros(n); kk = np.zeros(n)
    cap = p.overflow_stage_m * p.pit_area_m2
    vol, cum_in = 0.0, 0.0
    for i in range(n):
        q = q_rain[i] + q_fake[i]
        k_h = p.k0_per_h * np.exp(-p.clog_rate_per_m3 * cum_in)
        vol += q
        if p.drain_exponent == 1.0:
            out = vol * (1.0 - np.exp(-k_h / 60.0))
        else:   # outflow = k*A*h_ref*(h/h_ref)^beta, h_ref = 0.5 m, 6 explicit sub-steps per minute
            out, v = 0.0, vol
            for _ in range(6):
                hh = v / p.pit_area_m2
                d = min(v, k_h / 360.0 * p.pit_area_m2 * 0.5 * (max(hh, 0.0) / 0.5) ** p.drain_exponent)
                v -= d
                out += d
        vol -= out
        spill = vol - cap if vol > cap else 0.0
        vol -= spill
        h[i], infil[i], over[i], kk[i] = vol / p.pit_area_m2, out, spill, k_h
        cum_in += q_rain[i]
    truth = pd.DataFrame({"h_m": h, "inflow_rain_m3": q_rain, "inflow_fake_m3": q_fake, "infil_m3": infil,
                          "overflow_m3": over, "k_per_h": kk, "rain_mm": r}, index=idx)
    obs = np.clip(h + rng.normal(0.0, noise_m, n), 0.0, None)
    keep = rng.random(n) > 0.002
    observed = pd.DataFrame({"stage_m": obs[keep]}, index=idx[keep])
    return observed, truth
