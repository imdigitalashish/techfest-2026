#!/usr/bin/env python3
"""Ratchet driver for walkable-space (karpathy/autoresearch-style, parameter + code-switch hypotheses).

For each hypothesis (a patch to params.json): evaluate on split A; keep only if dJ_A >= NOISE and
dJ_B >= 0 on the confirmation split B; otherwise revert. Every trial is appended to results.tsv.
The evaluator (eval.py) is frozen; only params.json / walkable.py change.
Usage: python loop.py   (reads BACKLOG below; idempotent per run, appends to results.tsv)
"""
import datetime as dt
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from eval import run  # noqa: E402

NOISE = 0.03  # one held-out position (1/33) or one pair (1/40) is ~0.03 of J
PARAMS = os.path.join(HERE, "params.json")
TSV = os.path.join(HERE, "results.tsv")
BACKLOG = [
    ("trajectory gives connectivity only (no override of obstacle cells)", {"traj_override": False}),
    ("stricter floater removal: carve_beta 4 -> 2", {"carve_beta": 2.0}),
    ("keep more obstacle evidence: carve_beta 4 -> 8", {"carve_beta": 8.0}),
    ("narrower walked corridor: traj_radius 0.35 -> 0.20", {"traj_radius": 0.20}),
    ("safety margin: inflate obstacles by 5 cm", {"obstacle_inflate_m": 0.05}),
    ("single-point obstacles: min_occ_points 2 -> 1", {"min_occ_points": 1}),
    ("smaller hole closing: close_m 0.20 -> 0.10", {"close_m": 0.10}),
    ("wider floor evidence: floor_dilate_m 0.30 -> 0.50", {"floor_dilate_m": 0.50}),
]


def commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=HERE, text=True).strip()
    except Exception:
        return "nogit"


def log(row):
    new = not os.path.exists(TSV)
    with open(TSV, "a") as f:
        if new:
            f.write("timestamp\tcommit\thypothesis\tJ_A\tdelta_A\tJ_B\tdelta_B\tkept\tnotes\n")
        f.write("\t".join(str(x) for x in row) + "\n")


def main():
    cur = json.load(open(PARAMS))
    base_A, base_B = run(cur, "A"), run(cur, "B")
    log([dt.datetime.now().isoformat(timespec="seconds"), commit(), "BASELINE " + json.dumps(cur, sort_keys=True),
         f"{base_A['J']:.4f}", "", f"{base_B['J']:.4f}", "", "baseline",
         f"recall_A={base_A['recall_nav']:.3f} coll_A={base_A['path_collision_rate']:.3f} proxyhits_A={base_A['proxy_hits_at_heldout_cams']:.3f}"])
    print("baseline", base_A["J"], base_B["J"], flush=True)
    for hyp, patch in BACKLOG:
        trial = dict(cur)
        trial.update(patch)
        rA = run(trial, "A")
        dA = rA["J"] - base_A["J"]
        rB, dB = None, None
        if dA >= NOISE:
            rB = run(trial, "B")
            dB = rB["J"] - base_B["J"]
        kept = dA >= NOISE and dB is not None and dB >= 0
        log([dt.datetime.now().isoformat(timespec="seconds"), commit(), hyp + " " + json.dumps(patch),
             f"{rA['J']:.4f}", f"{dA:+.4f}", f"{rB['J']:.4f}" if rB else "", f"{dB:+.4f}" if dB is not None else "",
             "yes" if kept else "no",
             f"recall_A={rA['recall_nav']:.3f} coll_A={rA['path_collision_rate']:.3f} succ_A={rA['success']:.2f} area={rA['area_navigable_m2']:.1f}"])
        print(hyp, round(rA["J"], 4), round(dA, 4), "kept" if kept else "reverted", flush=True)
        if kept:
            cur, base_A, base_B = trial, rA, rB
            json.dump(cur, open(PARAMS, "w"), indent=1, sort_keys=True)
    print("final", json.dumps(cur, sort_keys=True), base_A["J"], base_B["J"])


if __name__ == "__main__":
    main()
