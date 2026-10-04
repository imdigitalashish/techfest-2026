"""C3 isolated metric: macro-F1 on Twitter Financial News Sentiment (validation split; HF zeroshot/, MIT).

    curl -L -o .data/tfns/sent_valid.csv \
      https://huggingface.co/datasets/zeroshot/twitter-financial-news-sentiment/resolve/main/sent_valid.csv
    PYTHONPATH=. .venv/bin/python components/text_scorer/eval_isolated.py [vader|minilm|minilm_noise0.2|finbert ...]
Labels: 0 bearish, 1 bullish, 2 neutral. VADER uses the standard +-0.05 compound thresholds.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score

OUT = Path(__file__).parent / "isolated_results.json"


def predict(name: str, texts: list[str]) -> np.ndarray:
    if name == "vader":
        from components.text_scorer.vader import VaderScorer
        c = VaderScorer().score(texts)["compound"].to_numpy()
        return np.where(c > 0.05, 1, np.where(c < -0.05, 0, 2))
    if name.startswith("minilm"):
        from components.text_scorer.minilm import MiniLMSentimentScorer
        noise = float(name.split("_noise")[1]) if "_noise" in name else 0.0
        return MiniLMSentimentScorer(label_noise=noise).proba(texts).argmax(1)  # [bearish, bullish, neutral]
    if name == "finbert":
        from components.text_scorer.finbert import FinBertScorer
        p = FinBertScorer(cache_dir=".cache").score(texts)[["p_neg", "p_pos", "p_neu"]].to_numpy()
        return p.argmax(1)  # neg->0 bearish, pos->1 bullish, neu->2 neutral
    raise ValueError(name)


def main(names: list[str]):
    df = pd.read_csv(".data/tfns/sent_valid.csv")
    y = df["label"].to_numpy(int)
    res = json.loads(OUT.read_text()) if OUT.exists() else {}
    for n in names:
        yhat = predict(n, df["text"].astype(str).tolist())
        res[n] = {"n": int(len(y)), "macro_f1": float(f1_score(y, yhat, average="macro")),
                  "accuracy": float(accuracy_score(y, yhat)),
                  "f1_per_class[bearish,bullish,neutral]": [float(v) for v in f1_score(y, yhat, average=None)]}
        print(n, json.dumps(res[n]))
    OUT.write_text(json.dumps(res, indent=2))


if __name__ == "__main__":
    main(sys.argv[1:] or ["vader"])
