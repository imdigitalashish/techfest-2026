"""FROZEN evaluator for the C6 ratchet loop — do not edit inside the loop.

Prints `METRIC <x>`: mean normalised policy value of the 'uplift' policy over seeds 0-2,
20,000 SYNTHETIC persons each, budget Rs 10 per eligible person. Secondary lines: best-arm rule,
women's share. Usage (from india71-t3-finance/): python components/targeting/autoresearch/eval.py
"""
import os
import pathlib
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402

import sakriya_paths  # noqa: F401,E402
from eval.targeting_eval import run  # noqa: E402

SEEDS = [int(s) for s in os.environ.get("AR_SEEDS", "0,1,2").split(",")]
res = [run(s, 20000, 10.0, verbose=False) for s in SEEDS]
u = [r["uplift"]["normalised"] for r in res]
print(f"METRIC {np.mean(u):.4f}")
print(f"uplift_sd {np.std(u, ddof=1) if len(u) > 1 else 0:.4f} | best_arm {np.mean([r['ate_best']['normalised'] for r in res]):.4f} | "
      f"women_share {np.mean([r['uplift']['women_share'] for r in res]):.3f} | seeds {SEEDS}")
