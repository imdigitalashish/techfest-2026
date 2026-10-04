"""End-to-end walking-skeleton evaluation on StockNet (time-ordered split). Reproduce:

    cd perceptron-p10-trusted-text-signal
    bash eval/fetch_data.sh                    # clone StockNet into .data/ (gitignored)
    PYTHONPATH=. .venv/bin/python eval/prepare.py
    PYTHONPATH=. .venv/bin/python eval/run_baselines.py

Writes eval/results/baseline_v0.json and eval/results/baseline_v0.md.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from mapie.regression import ConformalizedQuantileRegressor
from scipy.stats import spearmanr

from components.attack.inject import PUMP_TEMPLATE, attacked_text_features, inject, oracle_variants
from components.conformal.methods import _frame, aci_from_bounds, cqr, cqr_aci, cqr_offset, split_cp
from components.fusion.lgbm_quantile import FEATURE_SETS, TEXT_COLS, QuantileFusion, pinball
from components.robust_conformal.certify import CertifiedCQR, docs_lookup, ensemble_bounds, features_from_docs
from components.text_scorer.vader import VaderScorer
from eval.metrics import evaluate

ALPHA, SEED = 0.1, 0
TRAIN_END, CAL_END, TEST_END = "2014-12-31", "2015-06-30", "2016-03-31"
OUT = Path("eval/results")


def split(panel):
    d = panel["trade_date"]
    return (panel[d <= TRAIN_END], panel[(d > TRAIN_END) & (d <= CAL_END)], panel[(d > CAL_END) & (d <= TEST_END)])


def groups_for(panel, train):
    q1, q2 = train["rv20"].quantile([1 / 3, 2 / 3])
    key = pd.MultiIndex.from_frame(panel[["ticker", "trade_date"]])
    rv = pd.Series(np.where(panel["rv20"] <= q1, "low", np.where(panel["rv20"] <= q2, "mid", "high")), index=key)
    att = pd.Series(np.where(panel["n_docs"] == 0, "none", np.where(panel["n_docs"] < 5, "1-4", "5+")), index=key)
    return {"vol": rv, "tweets": att}


def sym_cqr_frame(model, test, X_override=None, method="cqr_sym", Q=None):
    t = test if X_override is None else X_override
    p = model.predict(t)
    return _frame(test, p["q_lo"] - Q, p["q_hi"] + Q, p["q_med"], method), p


def main(tag: str = "baseline_v0", suffix: str = "", scorer_name: str = "vader+fin", oracle: bool = True):
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    panel = pd.read_parquet(f".cache/panel{suffix}.parquet")
    docs = pd.read_parquet(f".cache/docs_scored{suffix}.parquet")
    train, cal, test = split(panel)
    G = groups_for(panel, train)
    res = {"meta": {"alpha": ALPHA, "seed": SEED, "train": [str(train.trade_date.min().date()), TRAIN_END],
                    "cal": [str(cal.trade_date.min().date()), CAL_END], "test": [str(test.trade_date.min().date()), TEST_END],
                    "n_train": len(train), "n_cal": len(cal), "n_test": len(test), "tickers": int(panel.ticker.nunique()),
                    "text_scorer": scorer_name}, "ablation": {}, "spike": {}, "attack": {}}
    models = {}
    for name, cols in FEATURE_SETS.items():
        m = QuantileFusion(cols, ALPHA, SEED).fit(train)
        models[name] = m
        p = m.predict(test)
        y = test["y"].to_numpy()
        has = test["n_docs"].to_numpy() > 0
        Q = cqr_offset(m, cal)
        r = {"pinball_mean": float(np.mean([pinball(y, p[c].to_numpy(), lv) for c, lv in zip(["q_lo", "q_med", "q_hi"], m.levels)])),
             "ic_spearman": float(spearmanr(p["q_med"], y).statistic),
             "ic_spearman_tweet_days": float(spearmanr(p["q_med"][has], y[has]).statistic),
             "cqr_offset_Q": Q}
        ivs = {"split": split_cp(m, cal, test), "cqr_mapie": cqr(m, cal, test),
               "cqr_sym": sym_cqr_frame(m, test, Q=Q)[0], "cqr_aci": cqr_aci(m, cal, test, gamma=0.01)}
        for meth, iv in ivs.items():
            r[meth] = evaluate(iv, test, ALPHA, G)
        res["ablation"][name] = r
        print(name, {k: round(v["coverage"], 4) for k, v in r.items() if isinstance(v, dict)},
              {k: round(v["mean_width"], 3) for k, v in r.items() if isinstance(v, dict)}, flush=True)

    # cross-check own symmetric CQR against MAPIE symmetric_correction=True
    fm = models["fusion"]
    c = ConformalizedQuantileRegressor(estimator=fm.mapie_estimators(), confidence_level=1 - ALPHA, prefit=True)
    c.conformalize(cal[fm.cols].to_numpy(float), cal["y"].to_numpy(float))
    _, iv_m = c.predict_interval(test[fm.cols].to_numpy(float), symmetric_correction=True)
    own, _ = sym_cqr_frame(fm, test, Q=cqr_offset(fm, cal))
    res["meta"]["own_vs_mapie_symmetric_cqr_max_abs_diff"] = float(np.max(np.abs(np.sort(np.c_[own.lo, own.hi], 1) - np.sort(iv_m[:, :, 0], 1))))

    # ---- spike: certified CQR on the fusion model ----
    Q = cqr_offset(fm, cal)
    test_docs = docs_lookup(docs, test)
    X = test[fm.cols].to_numpy(float)
    ti = [fm.cols.index(cn) for cn in TEXT_COLS]
    # soundness 1: degenerate box reproduces the model exactly
    dumps = [mm.booster_.dump_model() for mm in fm.models]
    lb, ub = ensemble_bounds(dumps[1], X, X)
    res["spike"]["degenerate_box_max_abs_err"] = float(max(np.max(np.abs(lb - fm.models[1].predict(X))), np.max(np.abs(ub - fm.models[1].predict(X)))))
    # soundness 2: recomputed features from docs match the aggregator's
    feat = np.stack([features_from_docs(s, w) for s, w in test_docs])
    res["spike"]["feature_recompute_max_abs_err"] = float(np.max(np.abs(feat - X[:, ti])))
    for k in (1, 2, 3, 5):
        cc = CertifiedCQR(fm, Q, k)
        lo, hi = cc.intervals(X, test_docs)
        iv = _frame(test, lo, hi, fm.models[1].predict(X), f"certified_k{k}")
        res["spike"][f"clean_k{k}"] = evaluate(iv, test, ALPHA, G)
        print("certified clean k", k, round(res["spike"][f"clean_k{k}"]["coverage"], 4), round(res["spike"][f"clean_k{k}"]["mean_width"], 3), flush=True)

    # ---- attacks (budget k=3) ----
    K = 3
    y = test["y"].to_numpy()
    base_iv, base_p = sym_cqr_frame(fm, test, Q=Q)
    base_cov_mask = (y >= base_iv["lo"].to_numpy()) & (y <= base_iv["hi"].to_numpy())
    pump_sent = float(VaderScorer().score([PUMP_TEMPLATE.format(cashtag="$XYZ")])["compound"].iloc[0])
    pump_trust = 0.05
    att_docs = [inject(s, w, K, pump_sent, pump_trust) for s, w in test_docs]
    Xa = X.copy()
    Xa[:, ti] = np.stack([features_from_docs(s, w) for s, w in att_docs])
    ta = test.copy()
    ta[fm.cols] = Xa
    van_iv, van_p = sym_cqr_frame(fm, test, X_override=ta, Q=Q, method="cqr_sym_pump")
    cc = CertifiedCQR(fm, Q, K)
    lo, hi = cc.intervals(Xa, att_docs)
    cert_iv = _frame(test, lo, hi, van_p["q_med"], "certified_pump")
    # soundness 3: clean features lie inside the box computed from attacked docs
    blo, bhi = cc.boxes(Xa, att_docs)
    inside = np.all((X[:, ti] >= blo[:, ti] - 1e-9) & (X[:, ti] <= bhi[:, ti] + 1e-9), axis=1)
    res["attack"]["pump"] = {"k": K, "pump_sentiment": pump_sent, "pump_trust": pump_trust,
                             "median_shift_mean": float(np.mean(van_p["q_med"] - base_p["q_med"])),
                             "median_shift_p95_abs": float(np.quantile(np.abs(van_p["q_med"] - base_p["q_med"]), 0.95)),
                             "clean_features_inside_box_frac": float(inside.mean()),
                             "vanilla_cqr": evaluate(van_iv, test, ALPHA, G), "certified": evaluate(cert_iv, test, ALPHA, G)}
    # oracle adversary over all variants within budget K
    van_ok = np.ones(len(test), bool)
    cert_ok = np.ones(len(test), bool)
    for v in (oracle_variants(K) if oracle else []):
        Xv = X.copy()
        Xv[:, ti] = attacked_text_features(test_docs, v)
        tv = test.copy()
        tv[fm.cols] = Xv
        ivv, _ = sym_cqr_frame(fm, test, X_override=tv, Q=Q)
        van_ok &= (y >= ivv["lo"].to_numpy()) & (y <= ivv["hi"].to_numpy())
        adocs = [inject(s, w, v[0], v[1], v[2]) for s, w in test_docs]
        lo, hi = cc.intervals(Xv, adocs)
        cert_ok &= (y >= lo) & (y <= hi)
    res["attack"]["oracle"] = {"skipped": True} if not oracle else {"k": K, "n_variants": len(oracle_variants(K)),
                               "clean_cqr_coverage": float(base_cov_mask.mean()),
                               "vanilla_cqr_adversarial_coverage": float(van_ok.mean()),
                               "certified_adversarial_coverage": float(cert_ok.mean()),
                               "certified_clean_width": res["spike"][f"clean_k{K}"]["mean_width"],
                               "vanilla_clean_width": float(np.mean(base_iv.hi - base_iv.lo))}

    # ---- spike config: certified box + ACI (CR-ACI), clean and under the pump attack ----
    dates = test["trade_date"].to_numpy()
    yc = cal["y"].to_numpy(float)
    Xc = cal[fm.cols].to_numpy(float)
    pc = fm.predict(cal)
    pv = fm.predict(test)
    c_lb, c_ub = np.minimum(pc.q_lo, pc.q_hi).to_numpy(), np.maximum(pc.q_lo, pc.q_hi).to_numpy()
    v_lb, v_ub = np.minimum(pv.q_lo, pv.q_hi).to_numpy(), np.maximum(pv.q_lo, pv.q_hi).to_numpy()
    va_lb, va_ub = np.minimum(van_p.q_lo, van_p.q_hi).to_numpy(), np.maximum(van_p.q_lo, van_p.q_hi).to_numpy()
    cal_docs = docs_lookup(docs, cal)
    crk_lb_c, crk_ub_c = cc.raw_bounds(Xc, cal_docs)
    crk_lb, crk_ub = cc.raw_bounds(X, test_docs)
    crk_lb_a, crk_ub_a = cc.raw_bounds(Xa, att_docs)
    runs = {"cqr_aci_clean": (c_lb, c_ub, v_lb, v_ub), "cqr_aci_pump": (c_lb, c_ub, va_lb, va_ub),
            "cr_aci_clean": (crk_lb_c, crk_ub_c, crk_lb, crk_ub), "cr_aci_pump": (crk_lb_c, crk_ub_c, crk_lb_a, crk_ub_a)}
    res["spike"]["cr_aci"] = {}
    for nm, (a, b, c_, d_) in runs.items():
        lo, hi = aci_from_bounds(a, b, yc, c_, d_, y, dates, ALPHA, 0.01)
        res["spike"]["cr_aci"][nm] = evaluate(_frame(test, lo, hi, pv["q_med"], nm), test, ALPHA, G)
        print(nm, round(res["spike"]["cr_aci"][nm]["coverage"], 4), round(res["spike"]["cr_aci"][nm]["mean_width"], 3), flush=True)
    res["meta"]["runtime_s"] = round(time.time() - t0, 1)
    (OUT / f"{tag}.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res["attack"]["oracle"], indent=2))
    print(json.dumps({k: v for k, v in res["spike"].items() if not isinstance(v, dict)}, indent=2))
    print("runtime", res["meta"]["runtime_s"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="baseline_v0")
    ap.add_argument("--scorer", choices=["vader", "finbert"], default="vader")
    ap.add_argument("--no-oracle", action="store_true")
    a = ap.parse_args()
    sfx = "" if a.scorer == "vader" else f"_{a.scorer}"
    main(a.tag, sfx, {"vader": "vader+fin", "finbert": "ProsusAI/finbert"}[a.scorer], not a.no_oracle)
