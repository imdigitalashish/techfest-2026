"""FROZEN evaluator for the execution-agent ratchet (frozen 4 Oct 2026 09:55 IST, before first use).

For each candidate: the mean paired ΔIS (bps) vs TWAP on VALIDATION seeds with synchronised
twins (lower is better). Line format per candidate:
  <label>\t<mean dIS bps>\tci95=[lo,hi]\twin=<rate>\town_dIS=<bps>\tinstant_dIS=<bps>\tn=<seeds>
Usage: .venv/bin/python components/execution_agent/autoresearch/eval.py candidates.json [--seeds 100:140]
candidates.json = one policy spec or a list of specs (see eval/policies/*.json); TWAP is added automatically.
"""
import argparse, json, multiprocessing as mp, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "eval"))
QTY = 4000


def boot(d, seed=0):
    bm = np.random.RandomState(seed).choice(d, size=(10000, len(d))).mean(1)
    return np.percentile(bm, 2.5), np.percentile(bm, 97.5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("candidates")
    ap.add_argument("--seeds", default="100:140")
    ap.add_argument("--rng-sync", default="per_wakeup", choices=["naive", "per_wakeup"])
    ap.add_argument("--workers", type=int, default=9)
    a = ap.parse_args()
    lo, hi = map(int, a.seeds.split(":"))
    assert 100 <= lo < hi <= 200, "validation seeds only"
    from run_experiment import run_seed
    cands = json.load(open(a.candidates))
    cands = cands if isinstance(cands, list) else [cands]
    cands = [c for c in cands if c.get("label") != "TWAP"]
    specs = [{"kind": "TWAP", "label": "TWAP"}] + cands
    jobs = [(s, specs, QTY, None, a.rng_sync) for s in range(lo, hi)]
    with mp.get_context("spawn").Pool(a.workers) as pool:
        rows = [r for rs in pool.imap_unordered(run_seed, jobs) for r in rs]
    by = {}
    for r in rows:
        by.setdefault(r["seed"], {})[r["label"]] = r
    for c in cands:
        L = c["label"]
        d = np.array([v[L]["is_bps"] - v["TWAP"]["is_bps"] for v in by.values()])
        own = np.array([v[L]["own_impact_bps"] - v["TWAP"]["own_impact_bps"] for v in by.values()])
        ins = np.array([v[L]["instant_bps"] - v["TWAP"]["instant_bps"] for v in by.values()])
        lo_, hi_ = boot(d)
        print(f"{L}\t{d.mean():.4f}\tci95=[{lo_:.4f},{hi_:.4f}]\twin={np.mean(d < 0):.3f}\t"
              f"own_dIS={own.mean():.4f}\tinstant_dIS={ins.mean():.4f}\tn={len(d)}", flush=True)


if __name__ == "__main__":
    main()
