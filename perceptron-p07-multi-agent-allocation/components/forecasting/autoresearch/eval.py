"""FROZEN evaluator for the C4+C5 spike (detector + forecaster). The ratchet loop never edits this file.

Score (lower is better) on DEV seeds 0-19 of scenario `shock+drift+spikes` (1-day horizon):
    score = MAE_all + MAE_post_shock
MAE_all        mean |forecast(t..t+5) - true rate| over all steps after a 60-step warm-up, all zones, H=6
MAE_post_shock same, restricted to the 120 steps after the shock onset and to the shocked zones
Secondary (printed, not optimised): false alarms per zone-day outside labelled change windows,
detection delay on the shocked zones (steps from onset to first alarm), runtime.
Usage:  python -m components.forecasting.autoresearch.eval [module:factory]
        default factory = components.forecasting.autoresearch.candidate:make
"""
from __future__ import annotations

import importlib
import sys
import time
from dataclasses import replace

import numpy as np

from components.scenarios.scenarios import SCENARIOS, build_trace, diurnal_profile, historical_shares

H, WARM, WIN, SEEDS = 6, 60, 120, range(0, 20)


def evaluate(factory) -> dict:
    cfg = replace(SCENARIOS["shock+drift+spikes"], horizon=1440)
    prof, shares = diurnal_profile(cfg), historical_shares(cfg)
    level = shares * cfg.total_rate
    mae_all, mae_shock, fa, delays = [], [], [], []
    t0 = time.perf_counter()
    for seed in SEEDS:
        tr = build_trace(cfg, seed)
        T, Z = tr.counts.shape
        fc = factory(prof, level.copy())
        on = [c for c in tr.change_points if c.kind == "shock_on"][0]
        zones = list(on.zones)
        err = np.zeros(T)
        err_sh = []
        for t in range(T - H):
            pred = fc.forecast(t, H).mean
            e = np.abs(pred - tr.rates[t:t + H])
            err[t] = e.mean()
            if on.t <= t < on.t + WIN:
                err_sh.append(e[:, zones].mean())
            fc.observe(t, tr.counts[t])
        mae_all.append(err[WARM:T - H].mean())
        mae_shock.append(float(np.mean(err_sh)))
        alarms = getattr(fc, "alarms", [])
        win = np.zeros((T, Z), bool)
        for c in tr.change_points:
            win[c.t:min(T, c.t + 60), list(c.zones)] = True
        fa.append(sum(1 for (t, z) in alarms if not win[t, z]) / (Z * T / 1440))
        hit = [t for (t, z) in alarms if z in zones and t >= on.t]
        delays.append((min(hit) - on.t) if hit else WIN)
    return dict(score=float(np.mean(mae_all) + np.mean(mae_shock)), mae_all=float(np.mean(mae_all)),
                mae_post_shock=float(np.mean(mae_shock)), false_alarms_per_zone_day=float(np.mean(fa)),
                detect_delay=float(np.mean(delays)), runtime_s=time.perf_counter() - t0)


if __name__ == "__main__":
    spec = sys.argv[1] if len(sys.argv) > 1 else "components.forecasting.autoresearch.candidate:make"
    mod, fn = spec.split(":")
    r = evaluate(getattr(importlib.import_module(mod), fn))
    print(f"SCORE {r['score']:.5f}")
    print(" ".join(f"{k}={v:.4f}" for k, v in r.items()))
