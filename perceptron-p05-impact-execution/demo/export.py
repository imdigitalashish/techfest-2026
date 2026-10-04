"""Export the demo's replay data by re-running deterministic ABIDES seeds with the committed P5 code.

Usage (from perceptron-p05-impact-execution/, after the README's venv + scripts/fetch_abides.sh):
  nice -n 10 .venv/bin/python demo/export.py            # seeds 100-129, ~10 min on one core
Writes demo/data/summary.js (all seeds: twin-gap paths and cost terms) and demo/data/showcase_<seed>.js
(top-5 ladders, mids and fills for the first three seeds of the block, not hand-picked). Per-seed results are
cached in .data/demo_export/ (gitignored), so an interrupted export resumes. Runs one world at a time and waits
while kern.memorystatus_level is below 30 (pauses below 25).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p5demo as D  # noqa: E402

TWAP = {"kind": "TWAP", "label": "TWAP"}
SIZES = [1000, 2000, 4000, 8000, 16000]
GRID_S = 5                     # summary gap paths: every 5 s from 09:35 (T1 = 1,200 s and NSR horizons included)
RES = os.path.join(D.ROOT, "eval", "results")


def wait_for_memory(log=print):
    lv = D.mem_level()
    if lv is None or lv >= 30:
        return
    log(f"memory guard: level {lv} < 30, waiting")
    while True:
        time.sleep(15)
        lv = D.mem_level()
        if lv is None or lv >= 30:
            return


def guard_between(log=print):
    lv = D.mem_level()
    if lv is not None and lv < 25:
        log(f"memory guard: level {lv} < 25, pausing")
        wait_for_memory(log)


def _clean(v):
    if isinstance(v, float) and not np.isfinite(v):
        return None
    return v


def arm_summary(st: dict) -> dict:
    keep = ("t1", "is_bps", "drift_bps", "own_bps", "instant_bps", "filled", "n_fills", "ident", "ident_ok",
            "top1_exact", "hold", "arrival")
    out = {k: _clean(st[k]) for k in keep}
    out["gap2"] = D.half_cents(st["path"][::GRID_S])
    return out


def run_seed(seed: int, showcase: bool, log=print) -> dict:
    """Synced ghost + TWAP at every size + impact-aware at 4,000; naive ghost + TWAP at 4,000."""
    t0 = time.time()
    out, show = {"seed": seed}, {}
    wait_for_memory(log)
    g = D.run_arm(seed, None, 0, "per_wakeup")
    arrival = float(g["res"].mid_at(np.array([D.START]))[0])
    base = int(round(arrival))
    if showcase:
        show["ghost"] = D.world_view(g, base)
    for q in SIZES:
        guard_between(log)
        tr = D.run_arm(seed, TWAP, q, "per_wakeup")
        st = D.pair_stats(g, tr)
        out[f"sync_{q}"] = arm_summary(st)
        if showcase:
            show[f"twap_{q}"] = dict(D.world_view(tr, base), fills=D.fills_view(st["fills"]),
                                     stats={k: out[f"sync_{q}"][k] for k in out[f"sync_{q}"] if k != "gap2"})
        del tr
    guard_between(log)
    ia = D.run_arm(seed, D.ia_spec(), 4000, "per_wakeup")
    st = D.pair_stats(g, ia)
    out["ia_4000"] = arm_summary(st)
    if showcase:
        show["ia_4000"] = dict(D.world_view(ia, base), fills=D.fills_view(st["fills"]),
                               stats={k: out["ia_4000"][k] for k in out["ia_4000"] if k != "gap2"})
    del ia, g
    guard_between(log)
    gn = D.run_arm(seed, None, 0, "naive")
    tn = D.run_arm(seed, TWAP, 4000, "naive")
    out["naive_4000"] = arm_summary(D.pair_stats(gn, tn))
    del gn, tn
    if showcase:
        out["show"] = dict(seed=seed, base=base, arrival=arrival, ladder_dt=D.LADDER_DT, worlds=show)
    log(f"seed {seed}: {time.time() - t0:.0f}s  T1 gap 4k sync {out['sync_4000']['t1']:+.1f}c "
        f"naive {out['naive_4000']['t1']:+.1f}c  identity {out['sync_4000']['ident']}")
    return out


def e10_means() -> dict:
    """Arm means of the committed E10 replication (the cold open's TWAP-vs-agent bars)."""
    rows = list(csv.DictReader(open(os.path.join(RES, "E10_replication_test.csv"))))
    tw = {r["seed"]: float(r["is_bps"]) for r in rows if r["label"] == "TWAP"}
    ia = {r["seed"]: float(r["is_bps"]) for r in rows if r["label"] == "IA_sched_only"}
    assert set(tw) == set(ia)
    return dict(n=len(tw), twap_is_mean=sum(tw.values()) / len(tw), ia_is_mean=sum(ia.values()) / len(ia),
                arm="IA_sched_only", source="eval/results/E10_replication_test.csv")


def js(name: str, obj) -> str:
    return f"window.{name} = " + json.dumps(obj, separators=(",", ":"), allow_nan=False) + ";\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="100:130")
    ap.add_argument("--showcase", default="100,101,102")
    ap.add_argument("--out", default=os.path.join(D.DEMO, "data"))
    a = ap.parse_args()
    lo, hi = map(int, a.seeds.split(":"))
    seeds, show = list(range(lo, hi)), [int(s) for s in a.showcase.split(",") if s]
    cache = os.path.join(D.ROOT, ".data", "demo_export")
    os.makedirs(cache, exist_ok=True)
    os.makedirs(a.out, exist_ok=True)
    per = {}
    for s in seeds:
        f = os.path.join(cache, f"seed_{s}.json")
        if os.path.exists(f):
            per[s] = json.load(open(f))
            if (s in show) == ("show" in per[s]):
                continue
        per[s] = run_seed(s, s in show)
        json.dump(per[s], open(f, "w"), separators=(",", ":"))

    arms = {}
    for arm in [f"sync_{q}" for q in SIZES] + ["ia_4000", "naive_4000"]:
        rows = [per[s][arm] for s in seeds]
        arms[arm] = {k: [r[k] for r in rows] for k in rows[0]}
    load = lambda f: json.load(open(os.path.join(RES, f)))  # noqa: E731
    meta = dict(generated=time.strftime("%Y-%m-%d %H:%M IST", time.localtime()), abides_commit="f9cbe51",
                seeds=seeds, sizes=SIZES, grid_s=GRID_S, t1_s=1200, horizon_s=1800, depth=D.DEPTH,
                showcase=show, policy_file="eval/policies/e8_ablation.json (IA_sched_only), twap_only.json",
                source="demo/export.py: committed run_world + tca on deterministic seeds")
    summary = dict(meta=meta, claims=load("claims.json"), scorecard=load("realism_scorecard.json"),
                   nsr=load("nsr_E4_nsr_naive_vs_E4_nsr_sync.json"), nsr_e1=load("nsr_E1_calib_train.json"),
                   e10=e10_means(), arms=arms)
    with open(os.path.join(a.out, "summary.js"), "w") as fh:
        fh.write(js("P5", summary))
    for s in show:
        with open(os.path.join(a.out, f"showcase_{s}.js"), "w") as fh:
            fh.write("window.P5_SHOW = window.P5_SHOW || {};\n" + js(f"P5_SHOW[{s}]", per[s]["show"]))
    sizes = {f: os.path.getsize(os.path.join(a.out, f)) for f in sorted(os.listdir(a.out))}
    print("wrote", {k: f"{v / 1e6:.2f} MB" for k, v in sizes.items()}, f"total {sum(sizes.values()) / 1e6:.2f} MB")


if __name__ == "__main__":
    os.environ.setdefault("TZ", "Asia/Kolkata")
    time.tzset()
    main()
