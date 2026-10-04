"""EXPLORATORY (after the pre-registered run; no decision weight): why does price-only predict the DJIA
open-to-close return so well (Spearman IC 0.355)? Measures continuation of the overnight gap.

    PYTHONPATH=. .venv/bin/python eval/exploratory_djia_gap.py   -> eval/results/exploratory_djia_gap.json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

p = pd.read_csv(".data/kaggle_djia/DJIA.csv", parse_dates=["Date"]).sort_values("Date").reset_index(drop=True)
gap = 100 * np.log(p["Open"].shift(-1) / p["Close"])
y = 100 * np.log(p["Close"].shift(-1) / p["Open"].shift(-1))
same = (p["Open"].shift(-1) - p["Close"]).abs() / p["Close"] < 1e-6
out = {}
for nm, m in {"train": p["Date"] <= "2012-12-31", "test": (p["Date"] > "2014-06-30") & (p["Date"] <= "2016-06-30")}.items():
    k = m & gap.notna() & y.notna()
    out[nm] = {"n": int(k.sum()), "frac_open_equals_prev_close": float(same[k].mean()),
               "spearman_gap_vs_y": float(spearmanr(gap[k], y[k]).statistic)}
Path("eval/results/exploratory_djia_gap.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out))
