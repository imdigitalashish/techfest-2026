"""FROZEN evaluator for the execution-agent ratchet. The loop never edits this file.

Prints one scalar: mean paired ΔIS (bps) of the candidate vs TWAP on VALIDATION seeds
(lower is better), then secondary metrics (95% bootstrap CI, win rate, own-impact bps).
Usage: .venv/bin/python components/execution_agent/autoresearch/eval.py candidate.json [--seeds 100:140] [--rng-sync naive]
candidate.json = one policy spec (see eval/policies/test.json).
"""
import argparse, json, multiprocessing as mp, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "eval"))
VAL_SEEDS = (100, 140)   # frozen: validation split only; test seeds 1000+ are never used here
QTY = 4000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("candidate")
    ap.add_argument("--seeds", default=f"{VAL_SEEDS[0]}:{VAL_SEEDS[1]}")
    ap.add_argument("--rng-sync", default="naive", choices=["naive", "per_wakeup"])
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    lo, hi = map(int, a.seeds.split(":"))
    assert 100 <= lo < hi <= 200, "validation seeds only"
    from run_experiment import run_seed
    cand = json.load(open(a.candidate))
    cand["label"] = "CAND"
    specs = [{"kind": "TWAP", "label": "TWAP"}, cand]
    jobs = [(s, specs, QTY, None, a.rng_sync) for s in range(lo, hi)]
    with mp.get_context("spawn").Pool(a.workers) as pool:
        rows = [r for rs in pool.imap_unordered(run_seed, jobs) for r in rs]
    by = {}
    for r in rows:
        by.setdefault(r["seed"], {})[r["label"]] = r
    d = np.array([v["CAND"]["is_bps"] - v["TWAP"]["is_bps"] for v in by.values()])
    own = np.array([v["CAND"]["own_impact_bps"] for v in by.values()])
    rs = np.random.RandomState(0)
    bm = rs.choice(d, size=(10000, len(d))).mean(1)
    print(f"{d.mean():.4f}")
    print(f"ci95=[{np.percentile(bm, 2.5):.4f},{np.percentile(bm, 97.5):.4f}] win={np.mean(d < 0):.3f} "
          f"own_impact_bps={own.mean():.4f} n={len(d)} rng_sync={a.rng_sync}")


if __name__ == "__main__":
    main()
