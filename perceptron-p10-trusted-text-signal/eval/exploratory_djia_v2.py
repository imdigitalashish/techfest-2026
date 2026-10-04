"""EXPLORATORY follow-ups to the pre-registered DJIA test (run after it; no decision weight; registered result unchanged).

(A) registered specification, re-run as a sanity check (must reproduce text_utility_djia_v1.json exactly);
(B) pre-open variant (gpt-6-sol review B3): drop the features that need the next session's official open (gap, abs_gap).
    The decision is then made before the open and executed with market-on-open / market-on-close orders;
(C) positive control (gpt-6-astra review #2): add a synthetic "useful text" feature z = |y| + N(0, (s * sd|y|)^2),
    s in {0.5, 1, 2}, to the fusion arm of the registered specification. Is the test able to detect value at all?

    PYTHONPATH=. P10_DEVICE=cpu nice -n 10 .venv/bin/python eval/exploratory_djia_v2.py   -> eval/results/exploratory_djia_v2.json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from eval.text_utility_djia import (ALPHA, CAL_END, DATA, PRICE_COLS, TEST_END, TEXT_COLS, TRAIN_END, block_bootstrap_mean,
                                    fit_intervals_lgbm, price_features, text_features, winkler_vec)


def compare(train, cal, test, price_cols, fusion_cols):
    y = test.y.to_numpy()
    W, cov = {}, {}
    for name, cols in {"price_only": price_cols, "fusion": fusion_cols}.items():
        pt, Q, _ = fit_intervals_lgbm(cols, train, cal, test)
        lo, hi = pt.q_lo.to_numpy() - Q, pt.q_hi.to_numpy() + Q
        W[name], cov[name] = winkler_vec(y, lo, hi), float(np.mean((y >= lo) & (y <= hi)))
    d = W["price_only"] - W["fusion"]
    boot = block_bootstrap_mean(d)
    return {"winkler_price_only": float(W["price_only"].mean()), "winkler_fusion": float(W["fusion"].mean()),
            "mean_improvement": float(d.mean()), "relative_improvement": float(d.mean() / W["price_only"].mean()),
            "p_one_sided": float(np.mean((boot - d.mean()) >= d.mean())),
            "coverage_price_only": cov["price_only"], "coverage_fusion": cov["fusion"]}


def main():
    from components.text_scorer.minilm import MiniLMEncoder, MiniLMSentimentScorer
    px = pd.read_csv(DATA / "DJIA.csv", parse_dates=["Date"])
    news = pd.read_csv(DATA / "Combined_News_DJIA.csv", parse_dates=["Date"])
    enc = MiniLMEncoder()
    tf = text_features(news.sort_values("Date").reset_index(drop=True), enc, MiniLMSentimentScorer(encoder=enc))
    p = price_features(px).merge(tf, on="Date", how="left").dropna(subset=PRICE_COLS + TEXT_COLS + ["y"]).reset_index(drop=True)
    p["ticker"], p["trade_date"] = "DJIA", p["Date"]
    d = p["Date"]
    train, cal, test = p[d <= TRAIN_END].copy(), p[(d > TRAIN_END) & (d <= CAL_END)].copy(), p[(d > CAL_END) & (d <= TEST_END)].copy()
    out = {"A_registered_rerun": compare(train, cal, test, PRICE_COLS, PRICE_COLS + TEXT_COLS)}
    pre = [c for c in PRICE_COLS if c not in ("gap", "abs_gap")]
    out["B_pre_open_no_gap"] = {"price_cols": pre, **compare(train, cal, test, pre, pre + TEXT_COLS)}
    rng = np.random.default_rng(0)
    out["C_positive_control"] = {}
    for s in (0.5, 1.0, 2.0):
        parts = []
        for part in (train, cal, test):
            q = part.copy()
            q["z_synth"] = q.y.abs() + rng.normal(0, s * p.y.abs().std(), len(q))
            parts.append(q)
        out["C_positive_control"][f"noise_{s}"] = compare(*parts, PRICE_COLS, PRICE_COLS + TEXT_COLS + ["z_synth"])
    Path("eval/results/exploratory_djia_v2.json").write_text(json.dumps(out, indent=2))
    for k, v in out.items():
        print(k, {a: (round(b, 4) if isinstance(b, float) else b) for a, b in v.items() if not isinstance(b, (dict, list))} or v)


if __name__ == "__main__":
    main()
