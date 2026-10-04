"""FROZEN evaluator for C5 recharge-verifier (the autoresearch loop must never edit this file).

Run:  innovatex-t1-groundwater/.venv/bin/python innovatex-t1-groundwater/components/recharge_verifier/autoresearch/eval.py [--split dev|holdout]
Needs: innovatex-t1-groundwater/.data/delhi_weather_hourly.csv (regenerate with components/data-ingest/fetch_delhi.py)

Splits (fixed seeds; pits are SIMULATED, rain is REAL ERA5 for central Delhi):
  dev      monsoon 2025 (15 Jun - 30 Sep), fleet seed 11, 40 pits
  holdout  monsoon 2024 (15 Jun - 30 Sep), fleet seed 22, 40 pits
The registry handed to the verifier is deliberately imperfect (as from a commissioning test):
  pit area +-5 %, catchment +-10 %, k_as_built +-10 %, runoff prior fixed at 0.75 (truth 0.6-0.9).

Primary scalar (lower is better): event_mdape = median absolute % error of infiltrated volume per
detected event, over events whose true infiltration >= 0.2 m3.
Secondary: season_total_abs_pct_err, coverage (share of true infiltration inside detected events),
clogging precision/recall (truth: final k/k0 < 0.5; predicted: last scored event clogging_index < 0.5),
fake recall (fake pour inside an 'implausible' event), false_implausible_rate (honest pits),
blocked recall ('no_inflow' after the blockage).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
COMP = HERE.parent
ROOT = COMP.parents[1]
sys.path.insert(0, str(COMP))
sys.path.insert(0, str(ROOT / "components" / "twin_simulator"))

import simulate as sim  # noqa: E402
import verifier  # noqa: E402

SPLITS = {"dev": ("2025-06-15", "2025-09-30 23:00", 11), "holdout": ("2024-06-15", "2024-09-30 23:00", 22)}
N_PITS = 40


def run(split: str) -> dict:
    start, end, seed = SPLITS[split]
    rng = np.random.default_rng(seed)
    rain_h = sim.load_rain(start, end)
    rain_m = sim.minute_rain(rain_h, rng)
    fleet = sim.make_fleet(N_PITS, seed, rain_m.index[0], rain_m.index[-1])
    ape, tot_pred, tot_true, covered = [], 0.0, 0.0, 0.0
    clog_tp = clog_fp = clog_fn = 0
    fake_hit = fake_n = 0
    honest_events = honest_impl = 0
    blocked_hit = blocked_n = 0
    deferred_n = detected_n = 0
    for p in fleet:
        obs, truth = sim.simulate_pit(p, rain_m, rng)
        reg = {"structure_id": p.structure_id,
               "pit_area_m2": p.pit_area_m2 * rng.uniform(0.95, 1.05),
               "catchment_m2": p.catchment_m2 * rng.uniform(0.9, 1.1),
               "runoff_coeff": 0.75,
               "overflow_stage_m": p.overflow_stage_m,
               "k_as_built_per_h": p.k0_per_h * rng.uniform(0.9, 1.1)}
        ev = verifier.verify(obs["stage_m"], rain_m, reg)
        true_total = float(truth["infil_m3"].sum())
        tot_true += true_total
        for e in ev:
            if e["verdict"] == "no_inflow":
                continue
            detected_n += 1
            deferred_n += e["verdict"] == "deferred"
            t_inf = float(truth.loc[e["t_start"]:e["t_end"], "infil_m3"].sum())
            covered += t_inf
            tot_pred += e["recharged_m3"]
            if t_inf >= 0.2:
                ape.append(abs(e["recharged_m3"] - t_inf) / t_inf * 100.0)
        final_ratio = truth["k_per_h"].iloc[-1] / p.k0_per_h
        scored = [e for e in ev if e["clogging_index"] is not None and e["verdict"] != "no_inflow"]
        pred_clog = bool(scored) and scored[-1]["clogging_index"] < 0.5
        true_clog = final_ratio < 0.5
        clog_tp += pred_clog and true_clog
        clog_fp += pred_clog and not true_clog
        clog_fn += (not pred_clog) and true_clog
        for t, _ in p.fakes:
            fake_n += 1
            fake_hit += any(e["verdict"] == "implausible" and e["t_start"] <= t <= e["t_end"] for e in ev)
        if p.kind in ("healthy", "clogging"):
            real = [e for e in ev if e["verdict"] != "no_inflow"]
            honest_events += len(real)
            honest_impl += sum(e["verdict"] == "implausible" for e in real)
        if p.inlet_blocked_from is not None:
            blocked_n += 1
            blocked_hit += any(e["verdict"] == "no_inflow" and e["t_start"] >= p.inlet_blocked_from for e in ev)
    prec = clog_tp / (clog_tp + clog_fp) if clog_tp + clog_fp else float("nan")
    rec = clog_tp / (clog_tp + clog_fn) if clog_tp + clog_fn else float("nan")
    return {
        "split": split, "pits": N_PITS, "rain_period": [start, end], "rain_total_mm": float(rain_h.sum()),
        "events_scored": len(ape),
        "event_mdape": float(np.median(ape)) if ape else float("nan"),
        "event_ape_p90": float(np.percentile(ape, 90)) if ape else float("nan"),
        "season_total_abs_pct_err": abs(tot_pred - tot_true) / tot_true * 100.0 if tot_true else float("nan"),
        "coverage": covered / tot_true if tot_true else float("nan"),
        "clogging_precision": prec, "clogging_recall": rec,
        "fake_recall": fake_hit / fake_n if fake_n else float("nan"), "fakes": fake_n,
        "false_implausible_rate": honest_impl / honest_events if honest_events else float("nan"),
        "blocked_recall": blocked_hit / blocked_n if blocked_n else float("nan"), "blocked_pits": blocked_n,
        # denominators (reporting only, added 4 Oct 2026 after the final-deck review D16; metrics unchanged)
        "counts": {k: int(v) for k, v in {"detected_event_windows": detected_n, "scored_windows_true_infil_ge_0.2m3": len(ape),
                   "honest_event_windows_healthy_or_clogging_pits": honest_events,
                   "implausible_among_honest": honest_impl, "deferred_windows": deferred_n,
                   "true_clogged_pits_final_k_lt_0.5": clog_tp + clog_fn, "clog_tp": clog_tp, "clog_fp": clog_fp,
                   "clog_fn": clog_fn, "fakes_caught": fake_hit, "fakes": fake_n}.items()},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev", choices=list(SPLITS))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    t = time.time()
    res = run(a.split)
    res["runtime_s"] = round(time.time() - t, 1)
    print(json.dumps(res, indent=1))
    print(f"METRIC event_mdape={res['event_mdape']:.3f}")
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
