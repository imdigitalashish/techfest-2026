"""Build the cached modelling panel: ingest → align → FinBERT → trust → aggregate → TS features.

Usage (from perceptron-p10-trusted-text-signal/):
    PYTHONPATH=. .venv/bin/python eval/prepare.py [--scorer vader|finbert]
Writes .cache/docs_scored{suffix}.parquet and .cache/panel{suffix}.parquet (gitignored);
suffix is "" for vader (default) and "_finbert" for FinBERT (ProsusAI/finbert).
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd

from components.aggregator.aggregate import aggregate
from components.align.calendar import assign_trade_date, leakage_count
from components.ingest.stocknet import load_prices, load_tweets
from components.text_scorer.finbert import FinBertScorer, score_docs
from components.text_scorer.vader import score_docs_vader
from components.trust_scorer.heuristic import score_trust
from components.ts_features.features import build_ts_features

ROOT = Path(".data/stocknet-dataset")
CACHE = Path(".cache")
START, END = pd.Timestamp("2014-01-01"), pd.Timestamp("2016-03-31")


def main(scorer: str = "vader") -> dict:
    sfx = "" if scorer == "vader" else f"_{scorer}"
    t0 = time.time()
    CACHE.mkdir(exist_ok=True)
    bars = load_prices(ROOT)
    tweets = load_tweets(ROOT)
    tickers = sorted(set(tweets["ticker"]) & set(bars["ticker"]))
    bars = bars[bars["ticker"].isin(tickers)]
    tweets = tweets[tweets["ticker"].isin(tickers)]
    days = pd.DatetimeIndex(sorted(bars["date"].unique()))
    aligned = assign_trade_date(tweets, days)
    leaks = leakage_count(aligned)
    assert leaks == 0, f"look-ahead leakage: {leaks} documents"
    t1 = time.time()
    scored = score_docs_vader(aligned) if scorer == "vader" else score_docs(aligned, FinBertScorer(cache_dir=CACHE))
    t2 = time.time()
    trusted = score_trust(scored)
    trusted.to_parquet(CACHE / f"docs_scored{sfx}.parquet", index=False)
    ts = build_ts_features(bars)
    ts = ts[(ts["trade_date"] >= START) & (ts["trade_date"] <= END)]
    text = aggregate(trusted, ts[["ticker", "trade_date"]])
    panel = ts.merge(text, on=["ticker", "trade_date"], how="left")
    panel.to_parquet(CACHE / f"panel{sfx}.parquet", index=False)
    stats = {"scorer": scorer, "tickers": len(tickers), "tweets": int(len(tweets)), "aligned_docs": int(len(aligned)),
             "leakage_docs": leaks, "panel_rows": int(len(panel)),
             "panel_rows_with_docs": int((panel["n_docs"] > 0).sum()),
             "first_day": str(panel["trade_date"].min().date()), "last_day": str(panel["trade_date"].max().date()),
             "scorer_seconds": round(t2 - t1, 1), "total_seconds": round(time.time() - t0, 1)}
    (CACHE / f"prepare_stats{sfx}.json").write_text(json.dumps(stats, indent=2))
    print(json.dumps(stats, indent=2))
    return stats


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--scorer", choices=["vader", "finbert"], default="vader")
    main(ap.parse_args().scorer)
