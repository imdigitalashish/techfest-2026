"""PRE-REGISTERED text-utility test on unseen data (eval/preregistration/2026-10-04-text-utility-djia.md).

Kaggle "Daily News for Stock Market Prediction" (top-25 r/worldnews headlines per day + DJIA OHLCV,
2008-08-08..2016-07-01). Question: does headline text improve calibrated 90% interval forecasts of the
next session's open-to-close DJIA log return over a price-only model? Frozen with the pre-registration;
any later change is a documented deviation.

    cd perceptron-p10-trusted-text-signal
    bash eval/fetch_djia.sh
    PYTHONPATH=. P10_DEVICE=cpu nice -n 10 .venv/bin/python eval/text_utility_djia.py            # real run
    PYTHONPATH=. P10_DEVICE=cpu .venv/bin/python eval/text_utility_djia.py --synthetic           # dry run
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import QuantileRegressor
from sklearn.preprocessing import StandardScaler

from components.conformal.methods import aci_from_bounds, conformal_quantile
from components.fusion.lgbm_quantile import QuantileFusion, pinball

ALPHA, SEED, BLOCK, B = 0.1, 0, 10, 10_000
TRAIN_END, CAL_END, TEST_END = "2012-12-31", "2014-06-30", "2016-06-30"
PRICE_COLS = ["r0", "r1", "r2", "r3", "r4", "rv5", "rv20", "pk", "vol_z", "intraday", "gap", "abs_gap", "rv_oc20", "dow"]
TEXT_COLS = ["sent_mean", "sent_std", "frac_bear", "abs_max", "novelty"]
_BYTES = re.compile(r"""^b(['"])(.*)\1$""", re.S)
DATA = Path(".data/kaggle_djia")


def clean_headline(h) -> str | None:
    if not isinstance(h, str) or not h.strip():
        return None
    m = _BYTES.match(h.strip())
    return (m.group(2) if m else h).strip() or None


def price_features(px: pd.DataFrame) -> pd.DataFrame:
    p = px.sort_values("Date").reset_index(drop=True).copy()
    lc = np.log(p["Close"])
    p["r0"] = 100 * lc.diff()
    for L in range(1, 5):
        p[f"r{L}"] = p["r0"].shift(L)
    p["rv5"] = p["r0"].rolling(5, min_periods=5).std()
    p["rv20"] = p["r0"].rolling(20, min_periods=20).std()
    p["pk"] = 100 * np.sqrt(np.log(p["High"] / p["Low"]) ** 2 / (4 * np.log(2)))
    lv = np.log1p(p["Volume"].astype(float))
    p["vol_z"] = (lv - lv.shift(1).rolling(20, min_periods=10).mean()) / (lv.shift(1).rolling(20, min_periods=10).std() + 1e-6)
    p["intraday"] = 100 * np.log(p["Close"] / p["Open"])
    p["rv_oc20"] = p["intraday"].rolling(20, min_periods=20).std()
    p["gap"] = 100 * np.log(p["Open"].shift(-1) / p["Close"])  # known at the open of t+1
    p["abs_gap"] = p["gap"].abs()
    p["dow"] = p["Date"].shift(-1).dt.dayofweek
    p["y"] = 100 * np.log(p["Close"].shift(-1) / p["Open"].shift(-1))  # next session open-to-close
    return p


def text_features(news: pd.DataFrame, encoder, scorer) -> pd.DataFrame:
    tops = [c for c in news.columns if c.startswith("Top")]
    rows, flat, owner = [], [], []
    for i, r in news.iterrows():
        hs = [h for h in (clean_headline(r[c]) for c in tops) if h]
        flat += hs
        owner += [i] * len(hs)
    emb = encoder.encode(flat)
    prob = scorer.clf.predict_proba(emb.astype(np.float64))[:, np.argsort(scorer.clf.classes_)]  # bear, bull, neu
    owner = np.asarray(owner)
    means = []
    for i in range(len(news)):
        idx = owner == i
        s = prob[idx, 1] - prob[idx, 0]
        m = emb[idx].mean(0) if idx.any() else np.zeros(emb.shape[1])
        means.append(m / (np.linalg.norm(m) + 1e-12))
        rows.append({"Date": news["Date"].iloc[i], "n_head": int(idx.sum()),
                     "sent_mean": float(s.mean()) if idx.any() else 0.0, "sent_std": float(s.std()) if idx.sum() > 1 else 0.0,
                     "frac_bear": float(np.mean(prob[idx].argmax(1) == 0)) if idx.any() else 0.0,
                     "abs_max": float(np.abs(s).max()) if idx.any() else 0.0})
    out = pd.DataFrame(rows).sort_values("Date").reset_index(drop=True)
    M = np.stack(means)[out.index.to_numpy()]
    nov = np.zeros(len(out))
    for t in range(len(out)):
        if t >= 5:
            ref = M[max(0, t - 20):t].mean(0)
            nov[t] = 1 - float(M[t] @ ref / (np.linalg.norm(ref) + 1e-12))
    out["novelty"] = nov
    return out


def winkler_vec(y, lo, hi, a=ALPHA):
    return (hi - lo) + (2 / a) * (lo - y) * (y < lo) + (2 / a) * (y - hi) * (y > hi)


def block_bootstrap_mean(d: np.ndarray, block=BLOCK, b=B, seed=SEED) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = len(d)
    nb = int(np.ceil(n / block))
    starts = rng.integers(0, n, size=(b, nb))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]).reshape(b, -1)[:, :n] % n  # circular blocks
    return d[idx].mean(1)


def fit_intervals_lgbm(cols, train, cal, test):
    m = QuantileFusion(cols, ALPHA, SEED).fit(train)
    pc, pt = m.predict(cal), m.predict(test)
    Q = conformal_quantile(np.maximum(pc.q_lo.to_numpy() - cal.y.to_numpy(), cal.y.to_numpy() - pc.q_hi.to_numpy()), ALPHA)
    return pt, Q, pc


def fit_intervals_linear(cols, train, cal, test):
    sc = StandardScaler().fit(train[cols])
    preds = {}
    for name, q in zip(["q_lo", "q_med", "q_hi"], (ALPHA / 2, 0.5, 1 - ALPHA / 2)):
        qr = QuantileRegressor(quantile=q, alpha=0.0, solver="highs").fit(sc.transform(train[cols]), train.y)
        preds[name] = (qr.predict(sc.transform(cal[cols])), qr.predict(sc.transform(test[cols])))
    lo_c, hi_c = np.minimum(preds["q_lo"][0], preds["q_hi"][0]), np.maximum(preds["q_lo"][0], preds["q_hi"][0])
    lo_t, hi_t = np.minimum(preds["q_lo"][1], preds["q_hi"][1]), np.maximum(preds["q_lo"][1], preds["q_hi"][1])
    Q = conformal_quantile(np.maximum(lo_c - cal.y.to_numpy(), cal.y.to_numpy() - hi_c), ALPHA)
    return lo_t - Q, hi_t + Q


def synthetic(n=1989, seed=1):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2008-08-08", periods=n)
    vol = np.exp(np.cumsum(rng.normal(0, 0.05, n)) * 0.3) * 0.01
    c = 11000 * np.exp(np.cumsum(rng.normal(0, vol)))
    o = c * np.exp(rng.normal(0, vol / 2))
    px = pd.DataFrame({"Date": dates, "Open": o, "High": np.maximum(o, c) * (1 + vol / 3), "Low": np.minimum(o, c) * (1 - vol / 3),
                       "Close": c, "Volume": rng.integers(1e8, 3e8, n), "Adj Close": c})
    words = ["markets rally on stimulus hopes", "war fears grow in region", "central bank holds rates", "protests spread in capital",
             "oil prices slump", "election result surprises analysts", "earthquake hits coastal city", "trade deal signed"]
    news = pd.DataFrame({"Date": dates, "Label": 0, **{f"Top{i}": [f"b'{words[j]}'" for j in rng.integers(0, len(words), n)] for i in range(1, 26)}})
    return px, news


def main(synthetic_run: bool = False):
    from components.text_scorer.minilm import MiniLMEncoder, MiniLMSentimentScorer
    if synthetic_run:
        px, news = synthetic()
        out_path = Path(".cache/text_utility_djia_SYNTHETIC_dryrun.json")
    else:
        px = pd.read_csv(DATA / "DJIA.csv", parse_dates=["Date"])
        news = pd.read_csv(DATA / "Combined_News_DJIA.csv", parse_dates=["Date"])
        out_path = Path("eval/results/text_utility_djia_v1.json")
    enc = MiniLMEncoder()
    scorer = MiniLMSentimentScorer(encoder=enc)
    tf = text_features(news.sort_values("Date").reset_index(drop=True), enc, scorer)
    p = price_features(px).merge(tf, on="Date", how="left")
    p = p.dropna(subset=PRICE_COLS + TEXT_COLS + ["y"]).reset_index(drop=True)
    p["ticker"], p["trade_date"] = "DJIA", p["Date"]
    d = p["Date"]
    train, cal, test = p[d <= TRAIN_END], p[(d > TRAIN_END) & (d <= CAL_END)], p[(d > CAL_END) & (d <= TEST_END)]
    y = test.y.to_numpy()
    q1, q2 = train.rv20.quantile([1 / 3, 2 / 3])
    hv = test.rv20.to_numpy() > q2
    res = {"meta": {"synthetic": synthetic_run, "n_train": len(train), "n_cal": len(cal), "n_test": len(test),
                    "train": [str(train.Date.min().date()), str(train.Date.max().date())],
                    "cal": [str(cal.Date.min().date()), str(cal.Date.max().date())],
                    "test": [str(test.Date.min().date()), str(test.Date.max().date())],
                    "target": "100*log(Close[t+1]/Open[t+1])", "alpha": ALPHA, "block": BLOCK, "B": B}, "models": {}}
    W, bounds = {}, {}
    for name, cols in {"price_only": PRICE_COLS, "fusion": PRICE_COLS + TEXT_COLS}.items():
        pt, Q, pc = fit_intervals_lgbm(cols, train, cal, test)
        lo, hi = pt.q_lo.to_numpy() - Q, pt.q_hi.to_numpy() + Q
        W[name] = winkler_vec(y, lo, hi)
        st = {}
        alo, ahi = aci_from_bounds(pc.q_lo.to_numpy(), pc.q_hi.to_numpy(), cal.y.to_numpy(), pt.q_lo.to_numpy(), pt.q_hi.to_numpy(),
                                   y, test.Date.to_numpy(), ALPHA, 0.01, stats=st)
        cov = (y >= lo) & (y <= hi)
        res["models"][name] = {
            "winkler": float(W[name].mean()), "coverage": float(cov.mean()), "mean_width": float(np.mean(hi - lo)),
            "coverage_high_vol": float(cov[hv].mean()), "cqr_offset_Q": float(Q),
            "pinball": {lv: pinball(y, pt[c].to_numpy(), q) for lv, c, q in
                        (("q05", "q_lo", ALPHA / 2), ("q50", "q_med", 0.5), ("q95", "q_hi", 1 - ALPHA / 2))},
            "ic_spearman_median": float(spearmanr(pt.q_med, y).statistic),
            "aci": {"coverage": float(np.mean((y >= alo) & (y <= ahi))), "mean_width": float(np.mean(np.maximum(ahi - alo, 0)[np.isfinite(ahi - alo)])),
                    "mean_day_err": st["mean_day_err"]}}
        llo, lhi = fit_intervals_linear(cols, train, cal, test)
        res["models"][name]["linear_qr"] = {"winkler": float(winkler_vec(y, llo, lhi).mean()),
                                            "coverage": float(np.mean((y >= llo) & (y <= lhi))), "mean_width": float(np.mean(lhi - llo))}
        bounds[name] = (llo, lhi)
    dlt = W["price_only"] - W["fusion"]
    boot = block_bootstrap_mean(dlt)
    p_one = float(np.mean((boot - dlt.mean()) >= dlt.mean()))
    dl_lin = winkler_vec(y, *bounds["price_only"]) - winkler_vec(y, *bounds["fusion"])
    boot_lin = block_bootstrap_mean(dl_lin)
    adds = bool(dlt.mean() > 0 and p_one < 0.05 and res["models"]["fusion"]["coverage"] >= 0.85)
    res["primary"] = {"mean_winkler_improvement": float(dlt.mean()), "relative_improvement": float(dlt.mean() / W["price_only"].mean()),
                      "p_one_sided": p_one, "boot_90ci_of_mean": [float(np.quantile(boot, 0.05)), float(np.quantile(boot, 0.95))],
                      "decision": "text adds value" if adds else "no evidence that text adds value"}
    res["secondary_linear_qr"] = {"mean_winkler_improvement": float(dl_lin.mean()),
                                  "p_one_sided": float(np.mean((boot_lin - dl_lin.mean()) >= dl_lin.mean()))}
    res["exploratory"] = {f"spearman_abs_y_vs_{c}": float(spearmanr(np.abs(y), test[c]).statistic) for c in TEXT_COLS}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(res, indent=2))
    print(json.dumps({"meta": res["meta"], "primary": res["primary"], "secondary_linear_qr": res["secondary_linear_qr"]}, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic", action="store_true")
    main(ap.parse_args().synthetic)
