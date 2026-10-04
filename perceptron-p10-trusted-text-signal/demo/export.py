"""Export the small, committed demo bundle (demo/bundle/) from the cached v2 MiniLM evaluation data.

Run from the project folder (needs the 657 MB StockNet fetch + `eval/prepare.py --scorer minilm` once; a fresh clone
does NOT need to run this, the bundle is committed):

    PYTHONPATH=. P10_DEVICE=cpu nice -n 10 .venv/bin/python demo/export.py [--src .cache]

Writes (all small): cal+test feature rows, per-post sentiment/trust for cal+test (no texts), the three LightGBM
quantile models as text (bit-exact round trip is verified), the MiniLM sentiment head as JSON (round trip verified),
the showcase days (selection rule below; tweet texts only for those days) and a manifest with checks + hashes.

Showcase selection rule (deterministic, stated on screen): a test stock-day is FLIPPABLE if the clean plain
(symmetric) CQR interval covers the realised return and at least one variant of the committed 53-variant
`oracle_grid(3)` makes plain CQR miss. From the flippable days take (a) the 3 silent days (no real posts) that need
the fewest injected posts, ties by date then ticker, one per ticker; (b) the 3 busiest days (most real posts), ties
by fewest posts needed then date, one per ticker.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd

from components.attack.inject import PUMP_TEMPLATE, inject_seq, oracle_grid
from components.conformal.methods import cqr_offset
from components.fusion.lgbm_quantile import FEATURE_SETS, TEXT_COLS, TS_COLS, QuantileFusion
from components.robust_conformal.certify import docs_lookup, features_from_docs
from components.text_scorer.minilm import MiniLMEncoder, MiniLMSentimentScorer
from eval.run_baselines import ALPHA, SEED, split

DEMO = Path(__file__).resolve().parent
BUNDLE = DEMO / "bundle"
COMMITTED = Path("eval/results/text_minilm_v2.json")
LEVEL_NAMES = ("q_lo", "q_med", "q_hi")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(src: Path):
    ist = dt.datetime.now(dt.timezone(dt.timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d %H:%M IST")
    BUNDLE.mkdir(parents=True, exist_ok=True)
    committed = json.loads(COMMITTED.read_text())
    panel = pd.read_parquet(src / "panel_minilm.parquet")
    docs = pd.read_parquet(src / "docs_scored_minilm.parquet")
    tr, cal, te = split(panel)
    checks = {}

    # --- models: refit exactly as eval/run_baselines.py (seed 0, deterministic) and dump as text ---
    fm = QuantileFusion(FEATURE_SETS["fusion"], ALPHA, SEED).fit(tr)
    Xall = pd.concat([cal, te])[fm.cols].to_numpy(float)
    worst = 0.0
    for name, m in zip(LEVEL_NAMES, fm.models):
        s = m.booster_.model_to_string()
        (BUNDLE / f"model_{name}.txt").write_text(s)
        b = lgb.Booster(model_str=(BUNDLE / f"model_{name}.txt").read_text())
        worst = max(worst, float(np.max(np.abs(b.predict(Xall) - m.predict(Xall)))))
        if b.dump_model()["tree_info"] != m.booster_.dump_model()["tree_info"]:
            raise SystemExit(f"tree dump differs after text round trip for {name}")
    checks["model_text_roundtrip_max_abs_pred_diff"] = worst
    if worst != 0.0:
        raise SystemExit(f"model text round trip is not bit-exact ({worst}); bundle the training rows instead")

    # --- feature rows (cal + test) and per-post scores (no texts) ---
    keep = ["ticker", "trade_date", *TS_COLS, *TEXT_COLS, "y", "n_docs"]
    ct = pd.concat([cal, te])[keep].reset_index(drop=True)
    ct.to_parquet(BUNDLE / "panel_caltest.parquet", index=False)
    d = docs[docs["trade_date"] > cal["trade_date"].min() - pd.Timedelta(days=1)]
    d = d[d["trade_date"] <= te["trade_date"].max()][["ticker", "trade_date", "sentiment", "trust"]]
    d.reset_index(drop=True).to_parquet(BUNDLE / "docs_caltest.parquet", index=False)
    checks["n_cal"], checks["n_test"], checks["n_docs_caltest"] = len(cal), len(te), len(d)

    # --- sentiment head: same training as the committed scorer (embeddings from the local cache) ---
    sc = MiniLMSentimentScorer(train_csv=".data/tfns/sent_train.csv", encoder=MiniLMEncoder(cache_dir=".cache"))
    head = {"encoder": "sentence-transformers/all-MiniLM-L6-v2", "trained_on": "zeroshot/twitter-financial-news-sentiment (MIT), sent_train.csv",
            "classes": sc.clf.classes_.tolist(), "coef": sc.clf.coef_.tolist(), "intercept": sc.clf.intercept_.tolist()}
    (BUNDLE / "scorer_head.json").write_text(json.dumps(head))
    pump_text = [PUMP_TEMPLATE.format(cashtag="$XYZ")]
    pump_live = float(sc.score(pump_text)["compound"].iloc[0])
    checks["pump_template_score_cached_embedding"] = pump_live
    checks["pump_template_score_committed"] = committed["attack"]["pump"]["pump_sentiment"]
    from sklearn.linear_model import LogisticRegression
    lr = LogisticRegression()
    lr.classes_, lr.coef_, lr.intercept_ = (np.array(head["classes"]), np.array(head["coef"]), np.array(head["intercept"]))
    lr.n_features_in_ = lr.coef_.shape[1]
    E = sc.enc.encode(pd.read_csv(".data/tfns/sent_train.csv")["text"].astype(str).tolist()[:500]).astype(np.float64)
    checks["head_json_roundtrip_max_abs_proba_diff"] = float(np.max(np.abs(lr.predict_proba(E) - sc.clf.predict_proba(E))))

    # --- flippable days (committed oracle grid, k = 3) and showcase selection ---
    Q = cqr_offset(fm, cal)
    X = te[fm.cols].to_numpy(float)
    y = te["y"].to_numpy()
    td = docs_lookup(docs, te)
    ti = [fm.cols.index(c) for c in TEXT_COLS]
    p = fm.predict(te)
    base = (y >= p.q_lo.to_numpy() - Q) & (y <= p.q_hi.to_numpy() + Q)
    ok = np.ones(len(te), bool)
    min_j = np.full(len(te), 99)
    for sv, tv in oracle_grid(3):
        Xv = X.copy()
        Xv[:, ti] = np.stack([features_from_docs(*inject_seq(a, b, sv, tv)) for a, b in td])
        a0, a2 = fm.models[0].predict(Xv), fm.models[2].predict(Xv)
        cov = (y >= np.minimum(a0, a2) - Q) & (y <= np.maximum(a0, a2) + Q)
        ok &= cov
        min_j = np.where(base & ~cov, np.minimum(min_j, len(sv)), min_j)
    checks["oracle_plain_cqr_coverage"] = float(ok.mean())
    checks["oracle_plain_cqr_coverage_committed"] = committed["attack"]["oracle"]["vanilla_cqr_oracle_coverage"]
    if abs(checks["oracle_plain_cqr_coverage"] - checks["oracle_plain_cqr_coverage_committed"]) > 1e-12:
        raise SystemExit("oracle coverage does not match the committed JSON")
    flip = base & ~ok
    nd = te["n_docs"].to_numpy()
    cand = te.assign(_min_j=min_j, _flip=flip, _date=te["trade_date"].dt.strftime("%Y-%m-%d"))
    cand = cand[cand["_flip"]]

    def pick(df, keys, asc):
        out, seen = [], set()
        for _, r in df.sort_values(keys, ascending=asc).iterrows():
            if r["ticker"] not in seen:
                seen.add(r["ticker"])
                out.append(r)
            if len(out) == 3:
                break
        return out

    silent = pick(cand[cand["n_docs"] == 0], ["_min_j", "_date", "ticker"], [True, True, True])
    busy = pick(cand[cand["n_docs"] > 0], ["n_docs", "_min_j", "_date"], [False, True, True])
    days = []
    for kind, rows in (("silent", silent), ("busy", busy)):
        for r in rows:
            dd = docs[(docs["ticker"] == r["ticker"]) & (docs["trade_date"] == r["trade_date"])]
            posts = [{"text": t, "sentiment": float(s), "trust": float(w), "followers": int(f), "age_days": int(a), "verified": bool(v)}
                     for t, s, w, f, a, v in zip(dd["text"], dd["sentiment"], dd["trust"], dd["user_followers"],
                                                 dd["user_age_days"], dd["user_verified"])]
            days.append({"ticker": r["ticker"], "date": r["_date"], "kind": kind, "n_real_posts": int(r["n_docs"]),
                         "min_injected_to_flip": int(r["_min_j"]), "posts": posts})
    showcase = {
        "rule": ("Flippable = clean plain CQR covers the realised return and >= 1 of the 53 committed oracle_grid(3) "
                 "variants (<= 3 injected posts) makes plain CQR miss. Showcase = 3 silent flippable days needing the fewest "
                 "injected posts (ties: date, ticker) + 3 busiest flippable days (ties: fewest posts, date); one per ticker."),
        "n_test": int(len(te)), "n_flippable": int(flip.sum()), "n_flippable_silent": int((flip & (nd == 0)).sum()),
        "frac_flippable": float(flip.mean()), "n_test_silent": int((nd == 0).sum()),
        "note": "Exploratory: computed on the StockNet test period, which was inspected during development.",
        "days": days}
    (BUNDLE / "showcase.json").write_text(json.dumps(showcase, indent=1))

    files = sorted(p for p in BUNDLE.iterdir() if p.is_file() and p.name != "manifest.json")
    manifest = {"exported": ist, "source": {f: sha(src / f) for f in ("panel_minilm.parquet", "docs_scored_minilm.parquet")},
                "committed_results": str(COMMITTED), "checks": checks,
                "files": {p.name: {"bytes": p.stat().st_size, "sha256": sha(p)} for p in files}}
    (BUNDLE / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print(json.dumps(checks, indent=1))
    print("flippable", showcase["n_flippable"], "silent", showcase["n_flippable_silent"],
          [(x["ticker"], x["date"], x["kind"], x["n_real_posts"], x["min_injected_to_flip"]) for x in days])
    print("bundle MB", round(sum(p.stat().st_size for p in BUNDLE.iterdir()) / 1e6, 2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=".cache", help="folder with panel_minilm.parquet and docs_scored_minilm.parquet")
    main(Path(ap.parse_args().src))
