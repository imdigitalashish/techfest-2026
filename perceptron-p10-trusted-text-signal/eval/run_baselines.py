"""End-to-end walking-skeleton evaluation on StockNet (time-ordered split). Reproduce:

    cd perceptron-p10-trusted-text-signal
    bash eval/fetch_data.sh                    # clone StockNet into .data/ (gitignored)
    PYTHONPATH=. nice -n 10 .venv/bin/python eval/prepare.py [--scorer minilm]
    PYTHONPATH=. nice -n 10 .venv/bin/python eval/run_baselines.py --tag baseline_v1 [--scorer minilm]
    PYTHONPATH=. .venv/bin/python eval/report.py baseline_v1

Writes eval/results/<tag>.json (render to Markdown with eval/report.py). Forecasts are issued after the
16:00 ET close of day t for the close-to-close log return of day t+1.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
from mapie.regression import ConformalizedQuantileRegressor
from scipy.stats import spearmanr

from components.attack.inject import PUMP_TEMPLATE, inject_seq, oracle_grid
from components.conformal.methods import _frame, aci_from_bounds, cqr, cqr_aci, cqr_offset, split_cp
from components.fusion.lgbm_quantile import FEATURE_SETS, TEXT_COLS, QuantileFusion, pinball
from components.robust_conformal.certify import CertifiedCQR, docs_lookup, ensemble_bounds, features_from_docs
from components.text_scorer.vader import VaderScorer
from components.trust_scorer.heuristic import trust_of
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


def template_sentiment(scorer: str) -> float:
    """Sentiment the deployed scorer assigns to the pump template."""
    t = [PUMP_TEMPLATE.format(cashtag="$XYZ")]
    if scorer == "minilm":
        from components.text_scorer.minilm import MiniLMSentimentScorer
        return float(MiniLMSentimentScorer().score(t)["compound"].iloc[0])
    if scorer == "vader":
        return float(VaderScorer().score(t)["compound"].iloc[0])
    raise NotImplementedError(f"pump-template scoring not implemented for scorer {scorer!r} (review N2)")


def main(tag: str = "baseline_v1", suffix: str = "", scorer_name: str = "vader+fin", oracle: bool = True, scorer: str = "vader",
         seed: int = 0):
    global SEED
    SEED = seed
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    panel = pd.read_parquet(f".cache/panel{suffix}.parquet")
    docs = pd.read_parquet(f".cache/docs_scored{suffix}.parquet")
    if os.environ.get("P10_SMOKE"):  # fast end-to-end check on 3 tickers; never used for reported results
        keep = sorted(panel["ticker"].unique())[:3]
        panel, docs = panel[panel["ticker"].isin(keep)], docs[docs["ticker"].isin(keep)]
        tag = "SMOKE_" + tag
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
        st = {}
        ivs = {"split": split_cp(m, cal, test), "cqr_mapie": cqr(m, cal, test),
               "cqr_sym": sym_cqr_frame(m, test, Q=Q)[0], "cqr_aci": cqr_aci(m, cal, test, gamma=0.01, stats=st)}
        for meth, iv in ivs.items():
            r[meth] = evaluate(iv, test, ALPHA, G)
        r["cqr_aci_stats"] = st
        res["ablation"][name] = r
        ev = {k: v for k, v in r.items() if isinstance(v, dict) and "coverage" in v}
        print(name, {k: round(v["coverage"], 4) for k, v in ev.items()}, {k: round(v["mean_width"], 3) for k, v in ev.items()}, flush=True)

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

    # ---- attacks (budget k=3). Forecasts are issued after the 16:00 ET close of day t for close t+1. ----
    K = 3
    y = test["y"].to_numpy()
    dates = test["trade_date"].to_numpy()
    cc = CertifiedCQR(fm, Q, K)
    base_iv, base_p = sym_cqr_frame(fm, test, Q=Q)
    base_cov_mask = (y >= base_iv["lo"].to_numpy()) & (y <= base_iv["hi"].to_numpy())

    def attacked(sv, tv):
        adocs = [inject_seq(s, w, sv, tv) for s, w in test_docs]
        Xv = X.copy()
        Xv[:, ti] = np.stack([features_from_docs(*d) for d in adocs])
        tv_ = test.copy()
        tv_[fm.cols] = Xv
        return adocs, Xv, tv_

    def certified_under(adocs, Xv, name, pred_med):
        lb, ub = cc.raw_bounds(Xv, adocs)
        iv = _frame(test, lb - Q, ub + Q, pred_med, name)
        ok = (y >= lb - Q) & (y <= ub + Q)
        return lb, ub, evaluate(iv, test, ALPHA, G), bool(np.all(ok[base_cov_mask]))

    # pump: K bullish posts from fresh accounts; sentiment and trust from the deployed scorers
    pump_sent = template_sentiment(scorer)
    pump_trust = float(trust_of(0, 1.0, False, 1)[0])
    att_docs, Xa, ta = attacked((pump_sent,) * K, (pump_trust,) * K)
    van_iv, van_p = sym_cqr_frame(fm, test, X_override=ta, Q=Q, method="cqr_sym_pump")
    crk_lb_a, crk_ub_a, cert_eval, floor_ok = certified_under(att_docs, Xa, "certified_pump", van_p["q_med"])
    blo, bhi = cc.boxes(Xa, att_docs)
    inside = np.all((X[:, ti] >= blo[:, ti]) & (X[:, ti] <= bhi[:, ti]), axis=1)
    res["attack"]["pump"] = {"k": K, "pump_sentiment": pump_sent, "pump_trust": pump_trust,
                             "median_shift_mean": float(np.mean(van_p["q_med"] - base_p["q_med"])),
                             "median_shift_p95_abs": float(np.quantile(np.abs(van_p["q_med"] - base_p["q_med"]), 0.95)),
                             "clean_features_inside_box_frac": float(inside.mean()), "floor_holds": floor_ok,
                             "vanilla_cqr": evaluate(van_iv, test, ALPHA, G), "certified": cert_eval}

    # oracle over a richer grid (plain CQR); the adversary knows y and picks the worst variant per row
    grid = oracle_grid(K) if oracle else []
    van_ok = np.ones(len(test), bool)
    per_variant = []
    for sv, tv in grid:
        _, _, tv_ = attacked(sv, tv)
        ivv, pv_ = sym_cqr_frame(fm, test, X_override=tv_, Q=Q)
        ok = (y >= ivv["lo"].to_numpy()) & (y <= ivv["hi"].to_numpy())
        van_ok &= ok
        per_variant.append({"sents": list(sv), "trusts": list(tv), "vanilla_coverage": float(ok.mean()),
                            "median_shift_mean_abs": float(np.mean(np.abs(pv_["q_med"] - base_p["q_med"])))})
    per_variant.sort(key=lambda r: r["vanilla_coverage"])
    worst = []
    for r in per_variant[:3]:
        adocs, Xv, tv_ = attacked(r["sents"], r["trusts"])
        ivv, pv_ = sym_cqr_frame(fm, test, X_override=tv_, Q=Q)
        lb_w, ub_w, ev, fl = certified_under(adocs, Xv, "certified_worst", pv_["q_med"])
        worst.append({**r, "vanilla_width": float(np.mean(ivv.hi - ivv.lo)), "certified_coverage": ev["coverage"],
                      "certified_width": ev["mean_width"], "floor_holds": fl})
        if len(worst) == 1:
            worst_bounds = (lb_w, ub_w, np.minimum(pv_.q_lo, pv_.q_hi).to_numpy(), np.maximum(pv_.q_lo, pv_.q_hi).to_numpy())
    # beyond the certified budget (astra #9): j > K copies of the worst fixed variant's posts; no guarantee applies
    beyond = []
    if oracle:
        w0 = per_variant[0]
        for j in (4, 6, 10):
            sv, tv = tuple(np.resize(w0["sents"], j)), tuple(np.resize(w0["trusts"], j))
            adocs, Xv, tv_ = attacked(sv, tv)
            ivv, pv_ = sym_cqr_frame(fm, test, X_override=tv_, Q=Q)
            _, _, ev, fl = certified_under(adocs, Xv, f"certified_k{K}_beyond_{j}", pv_["q_med"])
            beyond.append({"injected": j, "vanilla_coverage": float(np.mean((y >= ivv["lo"].to_numpy()) & (y <= ivv["hi"].to_numpy()))),
                           "certified_k3_coverage": ev["coverage"], "certified_k3_width": ev["mean_width"],
                           "certified_k3_covers_all_clean_covered_rows": fl})
    res["attack"]["beyond_budget"] = beyond
    res["attack"]["oracle"] = {"skipped": True} if not oracle else {
        "k": K, "grid_size": len(grid), "clean_cqr_coverage": float(base_cov_mask.mean()),
        "vanilla_cqr_oracle_coverage": float(van_ok.mean()),
        "certified_guaranteed_floor": float(base_cov_mask.mean()),
        "vanilla_clean_width": float(np.mean(base_iv.hi - base_iv.lo)),
        "certified_clean_width": res["spike"][f"clean_k{K}"]["mean_width"],
        "worst3": worst, "all_variants": per_variant}

    # ---- CR-ACI (certified box + our own ACI loop): clean, pump on every day, worst variant in bursts ----
    yc = cal["y"].to_numpy(float)
    Xc = cal[fm.cols].to_numpy(float)
    pc, pv = fm.predict(cal), fm.predict(test)
    c_lb, c_ub = np.minimum(pc.q_lo, pc.q_hi).to_numpy(), np.maximum(pc.q_lo, pc.q_hi).to_numpy()
    v_lb, v_ub = np.minimum(pv.q_lo, pv.q_hi).to_numpy(), np.maximum(pv.q_lo, pv.q_hi).to_numpy()
    va_lb, va_ub = np.minimum(van_p.q_lo, van_p.q_hi).to_numpy(), np.maximum(van_p.q_lo, van_p.q_hi).to_numpy()
    crk_lb_c, crk_ub_c = cc.raw_bounds(Xc, docs_lookup(docs, cal))
    crk_lb, crk_ub = cc.raw_bounds(X, test_docs)
    runs = {"cqr_aci_clean": (c_lb, c_ub, v_lb, v_ub), "cqr_aci_pump": (c_lb, c_ub, va_lb, va_ub),
            "cr_aci_clean": (crk_lb_c, crk_ub_c, crk_lb, crk_ub), "cr_aci_pump": (crk_lb_c, crk_ub_c, crk_lb_a, crk_ub_a)}
    burst_days = np.unique(dates)[np.r_[20:30, 80:90, 140:150]]  # pre-specified: three 10-day bursts
    burst = np.isin(dates, burst_days)
    if oracle:
        w_lb, w_ub, wv_lb, wv_ub = worst_bounds
        runs["cqr_aci_burst_worst"] = (c_lb, c_ub, np.where(burst, wv_lb, v_lb), np.where(burst, wv_ub, v_ub))
        runs["cr_aci_burst_worst"] = (crk_lb_c, crk_ub_c, np.where(burst, w_lb, crk_lb), np.where(burst, w_ub, crk_ub))
    res["spike"]["cr_aci"], res["spike"]["aci_stats"] = {}, {}
    gb = {**G, "burst": pd.Series(np.where(burst, "attacked", "clean"), index=pd.MultiIndex.from_frame(test[["ticker", "trade_date"]]))}
    for nm, (a, b, c_, d_) in runs.items():
        st = {}
        lo, hi = aci_from_bounds(a, b, yc, c_, d_, y, dates, ALPHA, 0.01, stats=st)
        res["spike"]["cr_aci"][nm] = evaluate(_frame(test, lo, hi, pv["q_med"], nm), test, ALPHA, gb)
        res["spike"]["aci_stats"][nm] = st
        print(nm, round(res["spike"]["cr_aci"][nm]["coverage"], 4), round(res["spike"]["cr_aci"][nm]["mean_width"], 3), flush=True)
    res["meta"]["runtime_s"] = round(time.time() - t0, 1)
    (OUT / f"{tag}.json").write_text(json.dumps(res, indent=2))
    print(json.dumps({k: v for k, v in res["attack"]["oracle"].items() if k not in ("all_variants", "worst3")}, indent=2))
    print(json.dumps({k: v for k, v in res["spike"].items() if not isinstance(v, dict)}, indent=2))
    print("runtime", res["meta"]["runtime_s"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="baseline_v1")
    ap.add_argument("--scorer", choices=["vader", "minilm", "finbert"], default="vader")
    ap.add_argument("--no-oracle", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    sfx = "" if a.scorer == "vader" else f"_{a.scorer}"
    main(a.tag, sfx, {"vader": "vader+fin", "minilm": "MiniLM-L6 + LR (TFNS)", "finbert": "ProsusAI/finbert"}[a.scorer], not a.no_oracle, a.scorer, a.seed)
