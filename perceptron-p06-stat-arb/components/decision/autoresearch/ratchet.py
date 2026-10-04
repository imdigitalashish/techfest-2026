"""Ratchet driver: for each hypothesis, rewrite candidate.py's CONFIG, run the FROZEN eval, keep the
change only if it beats the best metric by more than the bootstrap SE, else revert. Appends every
run to results.tsv, then re-checks the winner and the baseline on the fresh holdout day.
Usage: .venv/bin/python -m components.decision.autoresearch.ratchet
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(__file__)
CAND = os.path.join(HERE, "candidate.py")
TSV = os.path.join(HERE, "results.tsv")

HYPOTHESES = [
    ("H0 per-pair×cell threshold (baseline)", {"rule": "threshold", "by": ["pair_id", "fee_bps", "delta_ms"]}),
    ("H1 global per-cell threshold", {"rule": "threshold", "by": ["fee_bps", "delta_ms"]}),
    ("H2 EV, KM survival by pair", {"rule": "ev", "strata": ["pair_id"]}),
    ("H3 EV, KM by pair×edge bucket", {"rule": "ev", "strata": ["pair_id", "edge_bucket_s"]}),
    ("H4 EV pair×edge, lambda×2", {"rule": "ev", "strata": ["pair_id", "edge_bucket_s"], "lam_mult": 2.0}),
    ("H5 EV pair×edge, lambda×0.5", {"rule": "ev", "strata": ["pair_id", "edge_bucket_s"], "lam_mult": 0.5}),
    ("H6 GBM classifier P(win)·win − P(loss)·loss", {"rule": "gbm_clf", "iters": 200}),
    ("H7 GBM regressor of P&L bps (LEV)", {"rule": "gbm_reg", "iters": 200}),
    ("H8 threshold AND EV(pair×edge)", {"rule": "and", "by": ["pair_id", "fee_bps", "delta_ms"], "strata": ["pair_id", "edge_bucket_s"]}),
]


def set_config(cfg: dict) -> None:
    s = open(CAND).read()
    s = re.sub(r"^CONFIG = .*$", "CONFIG = " + json.dumps(cfg), s, count=1, flags=re.M)
    open(CAND, "w").write(s)


def run_eval(holdout: bool = False) -> dict:
    cmd = [sys.executable, "-m", "components.decision.autoresearch.eval"] + (["--holdout"] if holdout else [])
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip().splitlines()
    return json.loads(out[-1])


def main() -> None:
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    if not os.path.exists(TSV):
        open(TSV, "w").write("timestamp\tcommit\thypothesis\tmetric_usd\tdelta_vs_best\tkept\tnotes\n")
    best_cfg, best = None, None
    for name, cfg in HYPOTHESES:
        set_config(cfg)
        r = run_eval()
        m, se = r["metric"], r["boot_se"]
        kept = best is None or (m - best["metric"] > se)
        delta = 0.0 if best is None else m - best["metric"]
        note = f"n={r['n_trades']} hit={r['hit_rate']:.3f} bps={r['mean_bps']:.3f} se={se:.1f} all_trades={r['all_trades_metric']:.1f}"
        with open(TSV, "a") as f:
            f.write(f"{dt.datetime.now().isoformat(timespec='seconds')}\t{commit}\t{name}\t{m:.2f}\t{delta:+.2f}\t{'yes' if kept else 'no'}\t{note}\n")
        print(name, round(m, 2), "kept" if kept else "reverted", flush=True)
        if kept:
            best_cfg, best = cfg, r
    set_config(best_cfg)
    ho = run_eval(holdout=True)
    set_config(HYPOTHESES[0][1])
    base_ho = run_eval(holdout=True)
    set_config(best_cfg)
    with open(TSV, "a") as f:
        f.write(f"{dt.datetime.now().isoformat(timespec='seconds')}\t{commit}\tHOLDOUT 2026-10-01 best={json.dumps(best_cfg)}\t{ho['metric']:.2f}\t"
                f"{ho['metric'] - base_ho['metric']:+.2f}\tre-check\tH0 baseline holdout={base_ho['metric']:.2f}; best n={ho['n_trades']} hit={ho['hit_rate']:.3f}\n")
    print("HOLDOUT best", ho["metric"], "baseline", base_ho["metric"])


if __name__ == "__main__":
    main()
