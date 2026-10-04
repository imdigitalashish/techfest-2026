"""FROZEN evaluator for C6 attribution (the autoresearch loop must never edit this file).

Replay = REAL background + REAL wind, with a SIMULATED construction site and SIMULATED sensors:
  background PM10: CPCB/DPCC hourly at Major Dhyan Chand National Stadium (OpenAQ id 6929), via the OpenAQ archive
  wind, RH: ERA5 hourly at central Delhi via Open-Meteo
  SIMULATED: a 120 m x 120 m site (3x3 grid of ground sources), work 08–18 IST Mon–Sat, 30 % 'uncontrolled' days;
             Gaussian plume (Briggs urban, class D sigmas); wind meander (true plume direction = ERA5 + noise, larger in
             light wind); calm-wind pooling over the whole site; a road beside the W node; 4 sensors with random slope,
             offset, humidity growth, slow drift and noise; vane error ±10°.
  Emission rates are simulation parameters chosen so fence-line increments span ~10–500 µg/m³ (UNVERIFIED vs field data).
Truth = the site's own PM10 contribution at the most-impacted fence-line node (µg/m³).
Scalar (lower is better) = MAE over ALL hours of the held-out DEV period, abstentions scored as estimate 0.
Also printed: TEST-period scalar (lead's holdout check), MAE on non-abstained hours, coverage, CSI for truth > 50.

Run from this folder:  python eval.py [method|all] [n_seeds]   (default: methods.CANDIDATE, 5 seeds)
Evaluator v1 (4 Oct 08:05): mean ± sd over seeds SEED..SEED+n-1 (each seed redraws the site, plumes and sensors);
sensor slope drift bounded (±10 %/yr 1-sd, clipped to 0.5–1.5×); non-finite estimates count as abstentions.
v0 (single seed, unbounded 5 %/month drift) was flawed: its TEST numbers are not comparable; see results.tsv.
"""
import os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import methods  # noqa: E402

DATA = os.path.join(HERE, "..", "..", "..", ".data")
SEED = 20261004
L = 60.0  # half-width of the site (m)
GEOM = {"N": (0.0, L), "E": (L, 0.0), "S": (0.0, -L), "W": (-L, 0.0)}
SOURCES = [(x, y) for x in (-L / 2, 0, L / 2) for y in (-L / 2, 0, L / 2)]
DEV = ("2025-02-01", "2025-12-31")
TEST = ("2026-01-01", "2026-09-30")
EXCEED = 50.0


def load():
    bg = pd.read_parquet(os.path.join(DATA, "openaq", "station_6929.parquet"))["pm10"]
    bg = bg.where((bg > 0) & (bg < 1500)).dropna()
    met = pd.read_parquet(os.path.join(DATA, "openmeteo", "era5_28.61_77.21.parquet"))
    df = pd.DataFrame({"bg": bg}).join(met[["wind_speed_10m", "wind_direction_10m", "relative_humidity_2m"]], how="inner").dropna()
    df["ws"] = df["wind_speed_10m"] / 3.6  # km/h → m/s
    return df


def briggs_urban_d(x):
    return 0.16 * x / np.sqrt(1 + 0.0004 * x), 0.14 * x / np.sqrt(1 + 0.0003 * x)


def simulate(df, rng):
    n = len(df)
    idx = df.index
    work = (idx.hour >= 8) & (idx.hour < 18) & (idx.dayofweek < 6)
    days = idx.normalize()
    uday = days.unique()
    uncontrolled = pd.Series(rng.random(len(uday)) < 0.3, index=uday)
    q_day = pd.Series(np.where(uncontrolled.values, rng.lognormal(np.log(0.6), 0.4, len(uday)),
                               rng.lognormal(np.log(0.1), 0.4, len(uday))), index=uday)  # g/s PM10 (SIMULATED)
    Q = np.where(work, q_day.reindex(days).values * rng.lognormal(0, 0.5, n), 0.0) * 1e6  # µg/s
    ws = df["ws"].values
    meander = np.where(ws < 1.0, 60.0, 20.0)
    wd_true = (df["wind_direction_10m"].values + rng.normal(0, 1, n) * meander) % 360
    u = np.maximum(ws, 0.5)
    to = np.deg2rad((wd_true + 180) % 360)
    ue, un = np.sin(to), np.cos(to)
    site = {}
    for node, (rx, ry) in GEOM.items():
        c = np.zeros(n)
        for sx, sy in SOURCES:
            dx, dy = rx - sx, ry - sy
            x = dx * ue + dy * un
            y = -dx * un + dy * ue
            xs = np.maximum(x, 1.0)
            sy_, sz_ = briggs_urban_d(xs)
            c += np.where(x > 1.0, (Q / len(SOURCES)) / (np.pi * u * sy_ * sz_) * np.exp(-y ** 2 / (2 * sy_ ** 2)), 0.0)
        site[node] = c
    pool = np.where(ws < 0.5, Q / (0.5 * 2 * L * 10.0) * 0.3, 0.0)  # calm-wind pooling seen by every node
    for node in site:
        site[node] = site[node] + pool
    truth = np.max(np.stack(list(site.values()), 1), 1)
    traffic = np.where(np.isin(idx.hour, [8, 9, 10, 17, 18, 19, 20]), 1.0, np.where((idx.hour >= 23) | (idx.hour < 6), 0.3, 0.6))
    rh = np.clip(df["relative_humidity_2m"].values, 0, 98)
    t_days = (idx - idx[0]).total_seconds().values / 86400
    obs = pd.DataFrame(index=idx)
    for node in GEOM:
        true_conc = df["bg"].values * (1 + rng.normal(0, 0.03, n)) + site[node] + (20.0 * traffic if node == "W" else 0.0)
        drift = rng.normal(0, 0.10)  # fractional slope change per year (SIMULATED); bounded below
        slope = rng.uniform(0.75, 1.25) * np.clip(1 + drift * t_days / 365, 0.5, 1.5)
        kappa = 0.05 * rng.uniform(0.8, 1.2)
        meas = slope * true_conc * (1 + kappa * rh / (100 - rh)) + rng.normal(0, 6) + rng.normal(0, 1, n) * (0.05 * true_conc + 2)
        obs[f"raw_{node}"] = np.maximum(meas, 0)
    obs["rh"] = rh
    obs["ws_meas"] = ws * (1 + rng.normal(0, 0.1, n))
    obs["wd_meas"] = (wd_true + rng.normal(0, 10, n)) % 360
    return obs, truth


def score(est, abstain, truth, mask):
    abstain = abstain | ~np.isfinite(est)  # non-finite estimates count as abstentions (scored 0)
    est = np.where(np.isfinite(est), est, 0.0)
    e = np.where(abstain, 0.0, est)[mask]
    t = truth[mask]
    na = mask & ~abstain
    obs_ev, fc_ev = t > EXCEED, e > EXCEED
    h, m, f = (obs_ev & fc_ev).sum(), (obs_ev & ~fc_ev).sum(), (~obs_ev & fc_ev).sum()
    return {"scalar_MAE_all": float(np.mean(np.abs(e - t))), "MAE_non_abstained": float(np.mean(np.abs(est[na] - truth[na]))) if na.any() else float("nan"),
            "coverage": float(1 - abstain[mask].mean()), "CSI_gt50": float(h / max(1, h + m + f)), "n": int(mask.sum())}


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else methods.CANDIDATE
    n_seeds = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    df = load()
    names = list(methods.METHODS) if which == "all" else [which]
    res = {n: [] for n in names}
    for k in range(n_seeds):
        obs, truth = simulate(df, np.random.default_rng(SEED + k))
        dev = (obs.index >= DEV[0]) & (obs.index <= DEV[1] + " 23:00")
        test = (obs.index >= TEST[0]) & (obs.index <= TEST[1] + " 23:00")
        for name in names:
            est, abstain = methods.METHODS[name](obs, GEOM)
            est, abstain = np.asarray(est, float), np.asarray(abstain, bool)
            res[name].append((score(est, abstain, truth, dev), score(est, abstain, truth, test)))
    for name, rs in res.items():
        dv = np.array([r[0]["scalar_MAE_all"] for r in rs]); tv = np.array([r[1]["scalar_MAE_all"] for r in rs])
        dc = np.array([r[0]["CSI_gt50"] for r in rs]); tc = np.array([r[1]["CSI_gt50"] for r in rs])
        cov = np.mean([r[1]["coverage"] for r in rs])
        print(f"{name:14s} DEV scalar={dv.mean():.2f} ± {dv.std():.2f} | TEST scalar={tv.mean():.2f} ± {tv.std():.2f} | "
              f"CSI>50 dev {dc.mean():.2f} test {tc.mean():.2f} | cov {cov:.2f} | seeds={n_seeds}")


if __name__ == "__main__":
    main()
