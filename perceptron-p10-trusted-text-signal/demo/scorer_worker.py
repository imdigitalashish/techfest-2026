"""Live text scorer for the demo, in its own process (torch + LightGBM in one process segfaults on macOS).

Deployed scorer: the committed `MiniLMSentimentScorer.score` (frozen all-MiniLM-L6-v2 on CPU + the logistic-regression
head exported to bundle/scorer_head.json; round trip verified bit-exact by export.py). If the encoder cannot be loaded
offline, or P10_SCORER=vader, the committed `VaderScorer` is used instead and reported as a FALLBACK.
Protocol: one JSON object per line on stdin {"id", "texts"}; replies {"id", "compound", "scorer"} on stdout.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

DEMO = Path(__file__).resolve().parent


def load_minilm():
    from sklearn.linear_model import LogisticRegression

    from components.text_scorer.minilm import MiniLMEncoder, MiniLMSentimentScorer
    head = json.loads((DEMO / "bundle/scorer_head.json").read_text())
    lr = LogisticRegression()
    lr.classes_, lr.coef_, lr.intercept_ = np.array(head["classes"]), np.array(head["coef"]), np.array(head["intercept"])
    lr.n_features_in_ = lr.coef_.shape[1]
    sc = MiniLMSentimentScorer.__new__(MiniLMSentimentScorer)  # skip re-training; the head comes from the bundle
    sc.enc = MiniLMEncoder(cache_dir=DEMO / ".cache", device="cpu")
    sc.clf = lr
    import torch
    torch.set_num_threads(int(os.environ.get("P10_TORCH_THREADS", "2")))
    sc.score(["warm-up"])
    return sc, "MiniLM-L6 + LR head (deployed scorer, CPU)"


def load_vader():
    from components.text_scorer.vader import VaderScorer
    return VaderScorer(), "VADER + finance lexicon (FALLBACK — not the deployed scorer)"


def main():
    t0 = time.time()
    scorer, name, err = None, None, None
    if os.environ.get("P10_SCORER", "minilm") != "vader":
        try:
            scorer, name = load_minilm()
        except Exception as e:  # noqa: BLE001 — any failure falls back, and is reported
            err = f"MiniLM unavailable: {type(e).__name__}: {e}"[:300]
    if scorer is None:
        scorer, name = load_vader()
    kind = "minilm" if name.startswith("MiniLM") else "vader"
    print(json.dumps({"ready": True, "scorer": kind, "label": name, "load_s": round(time.time() - t0, 2), "error": err}), flush=True)
    for line in sys.stdin:
        req = None
        try:
            req = json.loads(line)
            comp = scorer.score([str(t) for t in req["texts"]])["compound"].clip(-1, 1).astype(float).tolist()
            print(json.dumps({"id": req["id"], "compound": comp, "scorer": kind}), flush=True)
        except Exception as e:  # noqa: BLE001
            print(json.dumps({"id": req.get("id") if isinstance(req, dict) else None, "error": str(e)[:300]}), flush=True)


if __name__ == "__main__":
    main()
