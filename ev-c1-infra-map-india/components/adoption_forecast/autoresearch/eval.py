"""FROZEN evaluator for C9 adoption_forecast (spike 2). The loop never edits this file.
Data: VAHAN State x Fuel, calendar years 2020-2025 (full years only), BEV = ELECTRIC(BOV) + PURE EV, all 36 states/UTs.
DEV: rolling one-step origins 2022->2023 and 2023->2024. HOLDOUT (lead only, --holdout): 2024->2025.
Metric (lower is better): mean over DEV origins of WAPE = sum|F-A| / sum A across states (registration-weighted).
Secondary: median state sMAPE; national total error. Keep a change only if it beats the best DEV WAPE by > 0.01.
Usage: .venv/bin/python -W ignore components/adoption_forecast/autoresearch/eval.py [--holdout]
"""
import argparse, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); COMP = os.path.dirname(HERE); R = os.path.abspath(os.path.join(COMP, "..", ".."))
sys.path.insert(0, COMP)
import forecaster  # noqa: E402
def load():
    bev, allv = {}, {}
    for y in range(2020, 2026):
        d = pd.read_csv(f"{R}/.data/vahan/raw/nat_state_fuel_{y}.csv").set_index("row_label")
        bev[y] = d[["ELECTRIC(BOV)", "PURE EV"]].sum(axis=1); allv[y] = d["TOTAL"]
    return pd.DataFrame(bev), pd.DataFrame(allv)
def score(bev, allv, origin):
    f = forecaster.forecast(bev[[y for y in bev.columns if y <= origin]], allv[[y for y in allv.columns if y <= origin]])
    a = bev[origin + 1]; fc = pd.Series(f).reindex(a.index).fillna(0).clip(lower=0)
    wape = float((fc - a).abs().sum() / a.sum())
    smape = float(np.median(200 * (fc - a).abs() / (fc.abs() + a.abs()).replace(0, np.nan)))
    nat = float(fc.sum() / a.sum() - 1)
    return wape, smape, nat
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--holdout", action="store_true"); a = ap.parse_args()
    bev, allv = load()
    dev = [score(bev, allv, o) for o in (2022, 2023)]
    print(f"METRIC dev_wape={np.mean([d[0] for d in dev]):.4f}")
    print(f"secondary dev_median_smape={np.mean([d[1] for d in dev]):.2f} dev_national_err={[round(d[2], 3) for d in dev]} params={forecaster.PARAMS}")
    if a.holdout:
        w, s, n = score(bev, allv, 2024)
        print(f"HOLDOUT 2024->2025 wape={w:.4f} median_smape={s:.2f} national_err={n:+.3f}")
if __name__ == "__main__":
    main()
