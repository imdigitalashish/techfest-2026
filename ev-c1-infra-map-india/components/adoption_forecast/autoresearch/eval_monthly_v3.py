"""FROZEN evaluator v3 for C9 (monthly VAHAN), after the 4 Oct 2026 reviews. The loop never edits this file.
Changes vs v2: (1) DEV and HOLDOUT target windows no longer overlap: DEV origins 2022-03 .. 2023-12 (8 quarterly origins,
targets end Dec 2024); HOLDOUT origins 2024-12 .. 2025-09 (4, targets Jan 2025 .. Sep 2026); 2024-03/06/09 are purged.
(2) A static guard refuses to evaluate if forecaster.py can read files, the network or other modules dynamically.
(3) The HOLDOUT is RETROSPECTIVE: its targets were already viewed in v2, so it is reported, never used to select.
The untouched test is prospective (PROSPECTIVE.md). Metric: mean DEV WAPE of next-12-month BEV registrations per state.
Usage: .venv/bin/python -W ignore components/adoption_forecast/autoresearch/eval_monthly_v3.py [--holdout]
"""
import argparse, os, re, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); COMP = os.path.dirname(HERE)
FORBIDDEN = r"\bopen\(|read_csv|read_parquet|read_excel|read_json|requests|urllib|socket|subprocess|os\.system|os\.popen|pathlib|glob|importlib|__import__|\beval\(|\bexec\(|\.data|eval_monthly|results"
src = open(os.path.join(COMP, "forecaster.py")).read()
if re.search(FORBIDDEN, src):
    sys.exit(f"REFUSED: forecaster.py contains forbidden access ({re.search(FORBIDDEN, src).group(0)!r})")
sys.path.insert(0, COMP); sys.path.insert(0, HERE)
import forecaster  # noqa: E402
from eval_monthly import load_monthly  # noqa: E402  (trusted loader; Oct 2026 partial excluded)
DEV = [pd.Period(p, "M") for p in ["2022-03", "2022-06", "2022-09", "2022-12", "2023-03", "2023-06", "2023-09", "2023-12"]]
HOLD = [pd.Period(p, "M") for p in ["2024-12", "2025-03", "2025-06", "2025-09"]]
assert max(DEV) + 12 < min(HOLD) + 1, "DEV and HOLDOUT target windows overlap"
def score(bev, allv, origin, params=None):
    f = forecaster.forecast_12m(bev.loc[:, :origin].copy(), allv.loc[:, :origin].copy(), params).clip(lower=0)
    a = bev.loc[:, origin + 1: origin + 12].sum(1)
    return float((f - a).abs().sum() / a.sum()), float(f.sum() / a.sum() - 1)
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--holdout", action="store_true"); a = ap.parse_args()
    bev, allv = load_monthly("bev"), load_monthly("all")
    dev = [score(bev, allv, o) for o in DEV]
    print(f"METRIC dev_wape={np.mean([d[0] for d in dev]):.4f}")
    print(f"secondary dev_national_err_mean={np.mean([d[1] for d in dev]):+.3f} params={forecaster.PARAMS_M}")
    if a.holdout:
        h = [score(bev, allv, o) for o in HOLD]
        print(f"HOLDOUT(retrospective) wape={np.mean([x[0] for x in h]):.4f} by_origin={[round(x[0], 3) for x in h]}")
if __name__ == "__main__":
    main()
