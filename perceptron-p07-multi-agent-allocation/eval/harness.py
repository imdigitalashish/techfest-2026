"""C10 — Evaluation harness: (policy x scenario x seed) grid with common random numbers.

Per episode metrics (all from the simulator's StepInfo stream):
  served_frac   served / arrivals                       (primary)
  lost_frac     abandoned / arrivals
  mean_wait     mean steps waited by served requests;  p95_wait from the wait histogram
  empty_per_srv empty repositioning hops per served request (cost of moving resources)
  shock_lost    requests lost in the 120 steps after the shock onset (resilience "triangle" area)
  shock_served  served fraction in that window
  recover_steps steps after onset until the 30-step rolling served fraction first reaches >= 0.90 (a common
                absolute bar for every policy); = window length (120) if never
  solve_ms_mean / p99 planner latency (look-ahead policies)
Usage:  python -m eval.harness --scenarios shock --policies reactive mpc-cusum --seeds 0-19 --out eval/results/x
"""
from __future__ import annotations

import argparse
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pandas as pd

from components.policies.policies import make_policy
from components.scenarios.scenarios import SCENARIOS, build_trace, diurnal_profile, historical_shares
from components.simulator.core import DispatchCore

WIN, ROLL = 120, 30
# real-trace replay (NYC TLC yellow taxi, July 2025, Manhattan-internal trips, thinned): test days, train days, event window
NYC = {"nyc-jul03-04": (["2025-07-03", "2025-07-04"], ["2025-07-01", "2025-07-02"],
                        (1440 + 21 * 60 + 30, 1440 + 23 * 60 + 30)),   # observed July 4 21:30-23:30 surge (cause UNVERIFIED)
       "nyc-jul10-11": (["2025-07-10", "2025-07-11"], ["2025-07-08", "2025-07-09"], None)}   # ordinary Thu-Fri (robustness)


def episode_meta(cfg, trace):
    prof = diurnal_profile(cfg)
    shares = historical_shares(cfg)
    level = shares * cfg.total_rate  # deseasonalised per-zone level from history
    return dict(grid=cfg.grid, n_zones=cfg.grid ** 2, od_prob=trace.od_prob, profile=prof, hist_shares=shares,
                init_level=level, init_level_raw=level, rates=trace.rates)


def run_episode(job: dict) -> dict:
    if job["scenario"].startswith("nyc"):
        from components.scenarios.nyc_tlc import build_nyc_trace
        test_days, train_days, _ = NYC[job["scenario"]]
        trace, meta = build_nyc_trace(test_days, train_days, seed=job["seed"])
        cfg = SimpleNamespace(name=job["scenario"], day=1440)
    else:
        cfg = SCENARIOS[job["scenario"]]
        if job.get("horizon"):
            cfg = replace(cfg, horizon=int(job["horizon"]))
        trace = build_trace(cfg, job["seed"])
        meta = episode_meta(cfg, trace)
    hop = int(job.get("hop_steps", 1))
    meta["hop_steps"] = hop
    meta["patience"] = int(job["patience"])
    core = DispatchCore(trace, n_agents=job["n_agents"], patience=job["patience"], init_seed=job["seed"],
                        init_shares=meta["hist_shares"], move_steps_per_hop=hop)
    kw = dict(job.get("policy_kw", {}))
    if job.get("legacy") and (job["policy"].startswith("mpc") or job["policy"].startswith("oracle")):
        kw.update(backend="scipy", abandon_aware=False)   # reproduces runs made before 2026-10-04 10:15 IST
    pol = make_policy(job["policy"], **kw)
    if not job["policy"].startswith("oracle"):
        meta = dict(meta, rates=None)   # true (or proxy) rates reach only the oracle
    pol.reset(meta)
    T = trace.horizon
    served = np.zeros(T, np.int64); lost = np.zeros(T, np.int64); arr = np.zeros(T, np.int64)
    wh = np.zeros(job["patience"], np.int64); empty = 0
    t0 = time.perf_counter()
    while not core.done:
        st = core.state()
        info = core.step(pol.act(st))
        pol.observe(info)
        t = st.t
        served[t], lost[t], arr[t] = info.served.sum(), info.lost.sum(), info.arrivals.sum()
        wh += info.wait_hist; empty += info.empty_moves
    wall = time.perf_counter() - t0
    S = served.sum()
    cdf = np.cumsum(wh) / max(1, wh.sum())
    out = dict(policy=pol.name, scenario=cfg.name, seed=job["seed"], horizon=T, n_agents=job["n_agents"],
               patience=job["patience"], hop_steps=hop,
               arrivals=int(arr.sum()), served=int(S), served_frac=S / max(1, arr.sum()),
               lost_frac=lost.sum() / max(1, arr.sum()), mean_wait=float((wh * np.arange(wh.size)).sum() / max(1, S)),
               p95_wait=int(np.searchsorted(cdf, 0.95)), empty_per_srv=empty / max(1, S), wall_s=wall,
               pending_frac=int((core.tail - core.head).sum()) / max(1, arr.sum()))   # still waiting at the horizon
    if hasattr(pol, "planner"):
        out["planner_backend"] = pol.planner.backend
    if hasattr(pol, "solve_ms") and pol.solve_ms:
        sm = np.array(pol.solve_ms)
        out.update(solve_ms_mean=float(sm.mean()), solve_ms_p99=float(np.percentile(sm, 99)))
    on = [c for c in trace.change_points if c.kind == "shock_on"]
    if on:  # per-shock window metrics, averaged over every shock in the run (identical to before for one shock)
        sl, ss, rs = [], [], []
        for c in on:
            ts = c.t
            w_s, w_a = served[ts:ts + WIN], arr[ts:ts + WIN]
            sl.append(int(lost[ts:ts + WIN].sum()))
            ss.append(w_s.sum() / max(1, w_a.sum()))
            k = np.ones(ROLL)
            roll = np.convolve(w_s, k, "valid") / np.maximum(1, np.convolve(w_a, k, "valid"))
            ok = np.flatnonzero(roll >= 0.90)
            rs.append(int(ok[0] + ROLL) if ok.size else WIN)
        out.update(shock_t=on[0].t, n_shocks=len(on), shock_lost=float(np.mean(sl)), shock_served=float(np.mean(ss)),
                   recover_steps=float(np.mean(rs)), recovered_frac=float(np.mean(np.array(rs) < WIN)))  # rs==WIN: censored
    if job["scenario"] in NYC and NYC[job["scenario"]][2] is not None:
        a, b = NYC[job["scenario"]][2]
        out.update(event_lost=int(lost[a:b].sum()), event_served=served[a:b].sum() / max(1, arr[a:b].sum()))
    D = cfg.day
    if T // D >= 2:  # batch means for long runs: served fraction per simulated day
        out["daily_served"] = json.dumps([round(float(served[d * D:(d + 1) * D].sum() / max(1, arr[d * D:(d + 1) * D].sum())), 5)
                                          for d in range(T // D)])
    if job.get("save_series"):
        out["series"] = dict(served=served.tolist(), lost=lost.tolist(), arr=arr.tolist())
    return out


def parse_seeds(s: str) -> list[int]:
    if "-" in s:
        a, b = s.split("-")
        return list(range(int(a), int(b) + 1))
    return [int(x) for x in s.split(",")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", nargs="+", default=["stationary", "shock", "drift", "shock+drift"])
    ap.add_argument("--policies", nargs="+", default=["static", "greedy", "reactive", "mpc-ewma", "mpc-cusum", "oracle"])
    ap.add_argument("--seeds", default="0-19")
    ap.add_argument("--n-agents", type=int, default=40)
    ap.add_argument("--patience", type=int, default=10)
    ap.add_argument("--horizon", type=int, default=0)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--out", default="eval/results/run")
    ap.add_argument("--legacy", action="store_true", help="planner as before 10:15 IST 4 Oct (scipy, no abandonment)")
    a = ap.parse_args()
    jobs = [dict(policy=p, scenario=sc, seed=sd, n_agents=a.n_agents, patience=a.patience, horizon=a.horizon,
                 legacy=a.legacy)
            for sc in a.scenarios for sd in parse_seeds(a.seeds) for p in a.policies]
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    csv = os.path.join(a.out, "episodes.csv")
    rows = []
    with ProcessPoolExecutor(a.workers) as ex:
        futs = [ex.submit(run_episode, j) for j in jobs]
        for f in as_completed(futs):
            rows.append(f.result())
            pd.DataFrame(rows).to_csv(csv, index=False)   # incremental: partial grids survive interruption
    df = pd.DataFrame(rows).sort_values(["scenario", "policy", "seed"])
    df.to_csv(csv, index=False)
    with open(os.path.join(a.out, "config.json"), "w") as f:
        json.dump(dict(vars(a), n_jobs=len(jobs), wall_s=time.time() - t0), f, indent=1)
    print(df.groupby(["scenario", "policy"])[["served_frac", "lost_frac", "mean_wait", "empty_per_srv"]].mean().round(4))
    print(f"{len(jobs)} episodes in {time.time() - t0:.0f}s -> {a.out}")


if __name__ == "__main__":
    main()
