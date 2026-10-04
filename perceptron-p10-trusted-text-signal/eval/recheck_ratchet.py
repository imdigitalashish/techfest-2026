"""Lead re-check of a ratchet config on the untouched test period (CR-ACI clean + pump; no oracle).

    PYTHONPATH=. .venv/bin/python eval/recheck_ratchet.py components/robust_conformal/autoresearch/config.json
Prints JSON; compare with baseline CR-ACI in eval/results/baseline_v0.md (89.5% / 5.233 clean, 89.7% / 5.247 pump).
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

from components.attack.inject import PUMP_TEMPLATE, inject
from components.conformal.methods import aci_from_bounds, cqr_offset
from components.fusion.lgbm_quantile import TEXT_COLS, TS_COLS, QuantileFusion
from components.robust_conformal.certify import CertifiedCQR, docs_lookup, features_from_docs
from components.text_scorer.vader import VaderScorer
from eval.run_baselines import ALPHA, split

K = 3


def main(cfg_path: str):
    cfg = json.loads(open(cfg_path).read())
    panel, docs = pd.read_parquet(".cache/panel.parquet"), pd.read_parquet(".cache/docs_scored.parquet")
    train, cal, test = split(panel)
    text_cols = [c for c in TEXT_COLS if c in cfg.get("text_cols", TEXT_COLS)]
    m = QuantileFusion(TS_COLS + text_cols, ALPHA, 0, cfg.get("lgbm", {})).fit(train)
    cc = CertifiedCQR(m, cqr_offset(m, cal), K)
    tdocs, cdocs = docs_lookup(docs, test), docs_lookup(docs, cal)
    X, Xc = test[m.cols].to_numpy(float), cal[m.cols].to_numpy(float)
    ti = [m.cols.index(c) for c in text_cols]
    pump = float(VaderScorer().score([PUMP_TEMPLATE.format(cashtag="$XYZ")])["compound"].iloc[0])
    adocs = [inject(s, w, K, pump, 0.05) for s, w in tdocs]
    Xa = X.copy()
    if ti:
        Xa[:, ti] = np.stack([features_from_docs(s, w) for s, w in adocs])[:, [TEXT_COLS.index(c) for c in text_cols]]
    y, yc, dates = test["y"].to_numpy(float), cal["y"].to_numpy(float), test["trade_date"].to_numpy()
    c_lb, c_ub = cc.raw_bounds(Xc, cdocs)
    out = {"config": cfg}
    for name, (XX, dd) in {"clean": (X, tdocs), "pump": (Xa, adocs)}.items():
        lb, ub = cc.raw_bounds(XX, dd)
        lo, hi = aci_from_bounds(c_lb, c_ub, yc, lb, ub, y, dates, ALPHA, cfg.get("aci_gamma", 0.01))
        out[f"cov_{name}"], out[f"width_{name}"] = float(np.mean((y >= lo) & (y <= hi))), float(np.mean(hi - lo))
    print(json.dumps(out))


if __name__ == "__main__":
    main(sys.argv[1])
