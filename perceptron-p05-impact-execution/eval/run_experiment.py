"""End-to-end experiment runner: paired counterfactual twins over many seeds.

Usage (from perceptron-p05-impact-execution/):
  .venv/bin/python eval/run_experiment.py --exp E3_test --seeds 1000:1200 --qty 4000 \
      --policies eval/policies/test.json --workers 6
Writes eval/results/<exp>.csv (one row per seed x policy) and .data/runs/<exp>/ (raw paths).
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import pickle
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for c in ("sim_env", "execution_agent", "tca", "impact_model"):
    sys.path.insert(0, os.path.join(ROOT, "components", c))

CFG = dict(side="SELL", start="09:35:00", end="09:55:00", n_slots=40, end_time="10:05:00")


def _setup():
    import sim_env  # noqa: F401


def run_seed(job):
    _setup()
    from execution_agent.policies import make_policy
    from sim_env.twins import run_null, run_treatment
    from sim_env.world import ns_at
    from tca import decompose_is, impact_path, implementation_shortfall

    seed, specs, qty, out_dir, rng_sync = job
    c = CFG
    t0 = time.time()
    null = run_null(seed, c["side"], c["start"], c["end"], c["n_slots"], c["end_time"], rng_sync=rng_sync)
    start_ns, end_ns = ns_at(c["start"]), ns_at(c["end"])
    dt_s = (end_ns - start_ns) / 1e9 / c["n_slots"]
    arrival = float(null.mid_at(np.array([start_ns]))[0])
    grid = start_ns + np.arange(0, 1801, dtype=np.int64) * 1_000_000_000
    pre_grid = ns_at("09:30:00") + np.arange(0, 300, dtype=np.int64) * 1_000_000_000
    edges = np.array([start_ns + k * int(dt_s * 1e9) for k in range(c["n_slots"] + 1)])
    slot_vol = np.histogram(null.tx_t, bins=edges, weights=null.tx_q)[0]
    rows, raw = [], dict(seed=seed, slot_vol=slot_vol, arrival=arrival, runs={})
    for spec in specs:
        label = spec.get("label", spec["kind"])
        pol = make_policy(spec, c["n_slots"], dt_s)
        t1 = time.time()
        tr = run_treatment(seed, pol, c["side"], qty, c["start"], c["end"], c["n_slots"], c["end_time"],
                           rng_sync=rng_sync)
        rec = tr.agent_record
        is_ = implementation_shortfall(rec["fills"], arrival, c["side"])
        dec = decompose_is(rec["fills"], [d[0] for d in rec["decisions"]], arrival, c["side"], tr, null)
        path = impact_path(tr, null, grid, c["side"])
        pre_eq = bool(np.allclose(tr.mid_at(pre_grid), null.mid_at(pre_grid), equal_nan=True))
        hold = {f"dpos_{k}": tr.holdings_by_type.get(k, 0) - null.holdings_by_type.get(k, 0)
                for k in set(tr.holdings_by_type) | set(null.holdings_by_type)}
        row = dict(seed=seed, label=label, qty=qty, rng_sync=rng_sync, filled=rec["filled"], n_fills=len(rec["fills"]),
                   arrival=arrival, arrival_treat=float(tr.mid_at(np.array([start_ns]))[0]),
                   pre_window_identical=pre_eq, window_volume_null=float(slot_vol.sum()),
                   impact_end_cents=float(path[1200]), impact_post5_cents=float(path[1500]),
                   impact_post10_cents=float(path[1800]), impact_mean_cents=float(np.nanmean(path[:1201])),
                   wall_s=round(time.time() - t1, 2), avg_px=is_["avg_px"], is_cents=is_["is_cents"], is_bps=is_["is_bps"], **dec, **hold)
        rows.append(row)
        raw["runs"][label] = dict(path=path.astype(np.float32), fills=rec["fills"],
                                  decisions=[d[:2] + (d[4], d[5]) for d in rec["decisions"]])
    if out_dir:
        with open(os.path.join(out_dir, f"seed_{seed}.pkl"), "wb") as f:
            pickle.dump(raw, f)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", required=True)
    ap.add_argument("--seeds", required=True, help="a:b (half-open)")
    ap.add_argument("--qty", type=int, default=4000)
    ap.add_argument("--policies", required=True, help="JSON file: list of policy specs")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--rng-sync", default="naive", choices=["naive", "per_wakeup"])
    a = ap.parse_args()
    lo, hi = map(int, a.seeds.split(":"))
    specs = json.load(open(a.policies))
    out_dir = os.path.join(ROOT, ".data", "runs", a.exp)
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(ROOT, "eval", "results"), exist_ok=True)
    jobs = [(s, specs, a.qty, out_dir, a.rng_sync) for s in range(lo, hi)]
    rows = []
    t0 = time.time()
    with mp.get_context("spawn").Pool(a.workers) as pool:
        for i, r in enumerate(pool.imap_unordered(run_seed, jobs)):
            rows.extend(r)
            if (i + 1) % 10 == 0:
                print(f"{i + 1}/{len(jobs)} seeds, {time.time() - t0:.0f}s", flush=True)
    import pandas as pd
    df = pd.DataFrame(rows).sort_values(["seed", "label"])
    out = os.path.join(ROOT, "eval", "results", f"{a.exp}.csv")
    df.to_csv(out, index=False, float_format="%.6g")
    print(f"wrote {out} ({len(df)} rows) in {time.time() - t0:.0f}s")
    print(df.groupby("label")[["is_bps", "drift_bps", "own_impact_bps", "instant_bps",
                               "impact_end_cents", "impact_post10_cents"]].mean().round(4).to_string())


if __name__ == "__main__":
    main()
