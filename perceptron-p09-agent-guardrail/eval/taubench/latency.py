"""Latency of the Tier-0 retail guard: CPU time per check, robust to load on a shared machine.

  python -m eval.taubench.latency        -> eval/results/taubench/latency__test.json

Wall-clock times recorded by run.py include scheduler waits, so they swing with machine load (load average ~10 on this
shared Mac). Here each held-out test call is checked R=7 times. We take per-call medians of CPU time
(time.process_time_ns) and of wall time, then report p50/p95 across calls, with the load average at run time.
"""
from __future__ import annotations

import json
import os
import statistics
import time
from pathlib import Path

from components.checker import taubench_retail as tr
from eval.provenance import code_sha256
from eval.taubench.replay import _load_tau, load_items
from eval.taubench.run import CONFIGS, pct

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "eval" / "results" / "taubench" / "latency__test.json"
R = 7


def main():
    items = load_items("test")
    products = _load_tau()[0]()["products"]
    res = {"method": f"per-call median over {R} repeats; p50/p95 across calls; CPU = time.process_time_ns",
           "load_average_1m_5m_15m": [round(x, 2) for x in os.getloadavg()], "n_calls": len(items),
           "code_sha256": code_sha256(), "configs": {}}
    for g, fields in CONFIGS.items():
        tr.SUMMARY_FIELDS = fields
        cpu, wall = [], []
        for it in items:
            data = {"orders": it["db"]["orders"], "users": it["db"]["users"], "products": products}
            c_s, w_s = [], []
            for _ in range(R):
                c0, w0 = time.process_time_ns(), time.perf_counter_ns()
                tr.guard(it["tool"], it["args"], it["user_turns"], it["observations"], it["auth_user_id"], data,
                         confirm_prompt=it.get("confirm_prompt", ""))
                c_s.append((time.process_time_ns() - c0) / 1e6)
                w_s.append((time.perf_counter_ns() - w0) / 1e6)
            cpu.append(statistics.median(c_s))
            wall.append(statistics.median(w_s))
        res["configs"][g] = {"cpu_ms_p50": round(pct(cpu, 0.5), 3), "cpu_ms_p95": round(pct(cpu, 0.95), 3),
                             "wall_ms_p50": round(pct(wall, 0.5), 3), "wall_ms_p95": round(pct(wall, 0.95), 3)}
        print(g, res["configs"][g], flush=True)
    OUT.write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
