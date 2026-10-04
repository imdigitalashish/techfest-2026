"""Reaction time of our own pipeline (the "compute" term of the latency budget).

1. Decision step (C8): LEV compiled with Numba (components/decision/compiled.py), trained exactly like the
   walk-forward LEV (train cells of 2026-09-01, 5 BTC legs), evaluated on every candidate of 2026-10-01.
   - in-kernel: each decide() call timed inside the Numba loop with mach_absolute_time (no Python);
   - from Python: perf_counter_ns around one decide() call (includes Numba dispatch), 200k calls.
   Exactness vs sklearn's predict is asserted on all rows.
2. Detector (C6, Numba event loop incl. the EWMA fair basis): wall time per market-data event, amortised over
   the whole 2026-10-01 day for the 5 walk-forward legs and for all 9 legs (no per-event distribution).
Usage: eval/run_guarded.sh .venv/bin/python -m eval.decision_timing
"""
from __future__ import annotations

import json
import platform
import subprocess
import time

import numpy as np
import polars as pl

from components.decision.autoresearch.rules import LEARN_X, fit_gbm_reg
from components.decision.compiled import RAW_FIELDS, build, make_timer, ns_per_tick
from components.detector.cross import _detect
from eval.falsification import cached_cells
from eval.run_baseline import load

LEGS9 = "binance_BTCUSDT,binance-futures_BTCUSDT,coinbase_BTC-USD,okex_BTC-USDT,okex-swap_BTC-USDT-SWAP,bybit_BTCUSDT,kraken_BTC-USD,bitstamp_BTCUSD,deribit_BTC-PERPETUAL".split(",")
LEGS5 = LEGS9[:5]


def q(a: np.ndarray, p: float) -> float:
    return float(np.quantile(a, p))


def detector_cost(date: str, legs_files: list[str]) -> dict:
    s = load(".data/tardis", date, legs_files).sort("ts_exch_us", maintain_order=True)
    legs = sorted(s["leg"].unique().to_list())
    idx = {l: i for i, l in enumerate(legs)}
    args = (s["ts_exch_us"].to_numpy(), s["leg"].replace_strict(idx, return_dtype=pl.Int32).to_numpy(), s["bid_px"].to_numpy(),
            s["ask_px"].to_numpy(), s["bid_sz"].to_numpy(), s["ask_sz"].to_numpy(), len(legs), 1.0, 60e6, 120e6, 30e6, 3_000_000)
    _detect(*args)  # warm (JIT cache)
    runs = []
    for _ in range(3):
        t0 = time.perf_counter()
        r = _detect(*args)
        runs.append(time.perf_counter() - t0)
    n = int(s.height)
    best = min(runs)
    return {"date": date, "n_legs": len(legs), "events": n, "episodes": int(r[0].shape[0]), "wall_s_best_of_3": best,
            "ns_per_event": best / n * 1e9, "events_per_s": n / best}


def main() -> None:
    tr, _ = cached_cells("2026-09-01")
    te, _ = cached_cells("2026-10-01")
    m = fit_gbm_reg(tr)["m"]
    predict_row, decide, raw_to_x, a = build(m)
    R = np.ascontiguousarray(te.select(RAW_FIELDS).to_numpy())
    X = te.select(LEARN_X).to_numpy()
    ref = m.predict(X)
    ticks = np.empty(R.shape[0], np.uint64)
    vals = np.empty(R.shape[0])
    timed = make_timer(decide)
    timed(R[:1000], ticks[:1000], vals[:1000])          # JIT warm-up
    acts = timed(R, ticks, vals)
    max_err = float(np.max(np.abs(vals - ref)))
    assert max_err < 1e-9, max_err
    ns = ticks.astype(np.float64) * ns_per_tick()
    # repeat in-kernel timing over 5 passes for stable quantiles
    passes = [ns]
    for _ in range(4):
        timed(R, ticks, vals)
        passes.append(ticks.astype(np.float64) * ns_per_tick())
    ns_all = np.concatenate(passes)
    # from Python, one call at a time (includes Numba dispatch)
    x = np.empty(13); xi = np.empty(13)
    n_py = 200_000
    py = np.empty(n_py)
    pc = time.perf_counter_ns
    for k in range(n_py):
        r = R[k % R.shape[0]]
        t0 = pc(); decide(r, x, xi); t1 = pc()
        py[k] = t1 - t0
    out = {
        "machine": {"platform": platform.platform(), "processor": platform.processor(), "ns_per_tick": ns_per_tick()},
        "model": {"n_trees": a["n_trees"], "n_nodes": a["n_nodes"], "train_rows": tr.height, "features": LEARN_X},
        "exactness_max_abs_err_bps": max_err, "test_rows": int(R.shape[0]), "acts": int(acts),
        "decision_in_kernel_ns": {"p50": q(ns_all, 0.5), "p90": q(ns_all, 0.9), "p99": q(ns_all, 0.99), "p999": q(ns_all, 0.999),
                                  "mean": float(ns_all.mean()), "n": int(ns_all.size), "tick_resolution_ns": ns_per_tick()},
        "decision_from_python_ns": {"p50": q(py, 0.5), "p90": q(py, 0.9), "p99": q(py, 0.99), "p999": q(py, 0.999), "n": n_py},
        "detector": [detector_cost("2026-10-01", LEGS5), detector_cost("2026-10-01", LEGS9)],
        "note": "Machine shared with other jobs (load not controlled); figures are upper bounds for a dedicated core.",
    }
    out["commit"] = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    out["command"] = "eval/run_guarded.sh .venv/bin/python -m eval.decision_timing"
    json.dump(out, open("eval/results/decision_timing.json", "w"), indent=1)
    k, p = out["decision_in_kernel_ns"], out["decision_from_python_ns"]
    lines = ["# Reaction time: compiled decision step and detector (Apple M5, shared machine)", "",
             f"LEV: {a['n_trees']} trees / {a['n_nodes']:,} nodes, trained on 2026-09-01 cells ({tr.height:,} rows); "
             f"evaluated on all {R.shape[0]:,} candidates of 2026-10-01. Max |compiled − sklearn| = {max_err:.1e} bps.", "",
             "| decision step (features + LEV + act) | p50 | p90 | p99 | p99.9 |", "|---|---|---|---|---|",
             f"| in-kernel, Numba (mach_absolute_time, {k['tick_resolution_ns']:.1f} ns ticks; {k['n']:,} calls) | {k['p50']/1e3:.2f} µs | {k['p90']/1e3:.2f} µs | {k['p99']/1e3:.2f} µs | {k['p999']/1e3:.2f} µs |",
             f"| one call from Python incl. dispatch ({p['n']:,} calls) | {p['p50']/1e3:.2f} µs | {p['p90']/1e3:.2f} µs | {p['p99']/1e3:.2f} µs | {p['p999']/1e3:.2f} µs |",
             "", "| detector (Numba event loop, amortised) | events | wall (best of 3) | ns / event | events / s |", "|---|---|---|---|---|"]
    for d in out["detector"]:
        lines.append(f"| {d['date']}, {d['n_legs']} legs | {d['events']:,} | {d['wall_s_best_of_3']:.2f} s | {d['ns_per_event']:.0f} | {d['events_per_s']:,.0f} |")
    lines += ["", out["note"], "", f"Commit `{out['commit']}` · `{out['command']}`", ""]
    open("eval/results/decision_timing.md", "w").write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
