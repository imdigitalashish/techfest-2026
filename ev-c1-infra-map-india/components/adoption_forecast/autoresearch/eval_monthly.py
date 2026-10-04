"""FROZEN evaluator v2 for C9 adoption_forecast on MONTHLY VAHAN data. The loop never edits this file.
Data: VAHAN State x Month Wise, Jan 2019 - Sep 2026 (Oct 2026 is partial and excluded); BEV = fuel filter
ELECTRIC(BOV) + PURE EV; all-fuel totals for share models. 36 states/UTs (missing rows = 0).
Task: forecast the NEXT 12 MONTHS of BEV registrations per state from a quarterly origin.
DEV origins: 2022-12 .. 2024-09 (8). HOLDOUT origins (lead only, --holdout): 2024-12 .. 2025-09 (4).
Metric (lower is better): mean over DEV origins of WAPE = sum|F-A| / sum A across states. Keep if < best - 0.01.
Usage: .venv/bin/python -W ignore components/adoption_forecast/autoresearch/eval_monthly.py [--holdout]
"""
import argparse, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); COMP = os.path.dirname(HERE); R = os.path.abspath(os.path.join(COMP, "..", ".."))
sys.path.insert(0, COMP)
import forecaster  # noqa: E402
MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
LAST = pd.Period("2026-09", "M")
def load_monthly(kind):
    base = pd.read_csv(f"{R}/.data/vahan/raw/nat_state_month_all_2025.csv").row_label
    cols = {}
    for y in range(2019, 2027):
        d = pd.read_csv(f"{R}/.data/vahan/raw/nat_state_month_{kind}_{y}.csv").set_index("row_label").reindex(base).fillna(0)
        for i, m in enumerate(MONTHS):
            per = pd.Period(f"{y}-{i + 1:02d}", "M")
            if per <= LAST:
                cols[per] = d[m].astype(float)
    return pd.DataFrame(cols)
DEV = [pd.Period(p, "M") for p in ["2022-12", "2023-03", "2023-06", "2023-09", "2023-12", "2024-03", "2024-06", "2024-09"]]
HOLD = [pd.Period(p, "M") for p in ["2024-12", "2025-03", "2025-06", "2025-09"]]
def score(bev, allv, origin, params=None):
    hist_b, hist_a = bev.loc[:, :origin], allv.loc[:, :origin]
    f = forecaster.forecast_12m(hist_b, hist_a, params).clip(lower=0)
    a = bev.loc[:, origin + 1: origin + 12].sum(1)
    return float((f - a).abs().sum() / a.sum()), float(f.sum() / a.sum() - 1)
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--holdout", action="store_true"); a = ap.parse_args()
    bev, allv = load_monthly("bev"), load_monthly("all")
    dev = [score(bev, allv, o) for o in DEV]
    print(f"METRIC dev_wape={np.mean([d[0] for d in dev]):.4f}")
    print(f"secondary dev_national_err_mean={np.mean([d[1] for d in dev]):+.3f} dev_wape_range=[{min(d[0] for d in dev):.3f},{max(d[0] for d in dev):.3f}] params={forecaster.PARAMS_M}")
    if a.holdout:
        h = [score(bev, allv, o) for o in HOLD]
        print(f"HOLDOUT wape={np.mean([x[0] for x in h]):.4f} by_origin={[round(x[0], 3) for x in h]} national_err={[round(x[1], 3) for x in h]}")
if __name__ == "__main__":
    main()
