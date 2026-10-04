"""FROZEN ratchet evaluator for the spike (C10). The loop must never edit this file.

Splits (all before the reported test period, which stays untouched by the loop):
  train 2014-01-02..2014-09-30 · calibration 2014-10-01..2014-12-31 · validation 2015-01-02..2015-06-30
Reads candidate settings from config.json (model params, text feature subset, ACI gamma).
Prints one scalar SCORE = mean width of CR-ACI (k=3) on clean validation data, plus a penalty of
50 x shortfall if clean or pump-attacked coverage falls below 0.895. Lower is better.

    cd perceptron-p10-trusted-text-signal
    PYTHONPATH=. .venv/bin/python components/robust_conformal/autoresearch/eval.py [config.json]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from components.attack.inject import PUMP_TEMPLATE, inject
from components.conformal.methods import aci_from_bounds, cqr_offset
from components.fusion.lgbm_quantile import TEXT_COLS, TS_COLS, QuantileFusion
from components.robust_conformal.certify import CertifiedCQR, docs_lookup, features_from_docs
from components.text_scorer.vader import VaderScorer

HERE = Path(__file__).parent
ALPHA, K, FLOOR = 0.1, 3, 0.895


def main(cfg_path: Path = HERE / "config.json") -> float:
    cfg = json.loads(cfg_path.read_text())
    panel = pd.read_parquet(".cache/panel.parquet")
    docs = pd.read_parquet(".cache/docs_scored.parquet")
    d = panel["trade_date"]
    train = panel[d <= "2014-09-30"]
    cal = panel[(d > "2014-09-30") & (d <= "2014-12-31")]
    val = panel[(d > "2014-12-31") & (d <= "2015-06-30")]
    text_cols = [c for c in TEXT_COLS if c in cfg.get("text_cols", TEXT_COLS)]
    m = QuantileFusion(TS_COLS + text_cols, ALPHA, 0, cfg.get("lgbm", {})).fit(train)
    cc = CertifiedCQR(m, cqr_offset(m, cal), K)
    vdocs, cdocs = docs_lookup(docs, val), docs_lookup(docs, cal)
    X, Xc = val[m.cols].to_numpy(float), cal[m.cols].to_numpy(float)
    ti = [m.cols.index(c) for c in text_cols]
    pump = float(VaderScorer().score([PUMP_TEMPLATE.format(cashtag="$XYZ")])["compound"].iloc[0])
    adocs = [inject(s, w, K, pump, 0.05) for s, w in vdocs]
    Xa = X.copy()
    if ti:
        feats = np.stack([features_from_docs(s, w) for s, w in adocs])
        Xa[:, ti] = feats[:, [TEXT_COLS.index(c) for c in text_cols]]
    y, yc, dates = val["y"].to_numpy(float), cal["y"].to_numpy(float), val["trade_date"].to_numpy()
    c_lb, c_ub = cc.raw_bounds(Xc, cdocs)
    out = {}
    for name, (XX, dd) in {"clean": (X, vdocs), "pump": (Xa, adocs)}.items():
        lb, ub = cc.raw_bounds(XX, dd)
        lo, hi = aci_from_bounds(c_lb, c_ub, yc, lb, ub, y, dates, ALPHA, cfg.get("aci_gamma", 0.01))
        out[f"cov_{name}"] = float(np.mean((y >= lo) & (y <= hi)))
        out[f"width_{name}"] = float(np.mean(hi - lo))
    short = max(0.0, FLOOR - out["cov_clean"]) + max(0.0, FLOOR - out["cov_pump"])
    score = out["width_clean"] + 50 * short
    print(json.dumps({"SCORE": round(score, 5), **{k: round(v, 5) for k, v in out.items()}}))
    return score


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "config.json")
