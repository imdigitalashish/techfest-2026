"""C3 text scorer — per-document financial sentiment with FinBERT (ProsusAI/finbert, Apache-2.0).

sentiment = p_pos - p_neg in [-1, 1]. Scores are cached by text hash in .cache/sentiment_<model>.parquet,
so re-scoring the same corpus (or injected attack texts) is cheap and deterministic.
Isolated metric: macro-F1 on a labelled financial-tweet set (see research/components/text_scorer.md).
"""
from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd

from architecture.contracts.contracts import SCORED_DOCS, validate

DEFAULT_MODEL = "ProsusAI/finbert"
_URL = re.compile(r"https?://\S+|http\S*…?")
_USER = re.compile(r"@\w+")
_WS = re.compile(r"\s+")


def clean_text(t: str) -> str:
    t = _URL.sub("URL", t)
    t = _USER.sub("@user", t)
    return _WS.sub(" ", t).strip()


def _h(t: str) -> str:
    return hashlib.sha1(t.encode("utf-8")).hexdigest()


class FinBertScorer:
    def __init__(self, model: str = DEFAULT_MODEL, cache_dir: str | os.PathLike = ".cache",
                 batch_size: int = 256, max_length: int = 64, device: str | None = None):
        self.model_name = model
        self.batch_size, self.max_length = batch_size, max_length
        self.cache_path = Path(cache_dir) / f"sentiment_{model.replace('/', '__')}.parquet"
        self._device = device
        self._tok = self._mdl = None

    def _load(self):
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        dev = self._device or os.environ.get("P10_DEVICE") or ("mps" if torch.backends.mps.is_available() else "cpu")
        self._tok = AutoTokenizer.from_pretrained(self.model_name)
        self._mdl = AutoModelForSequenceClassification.from_pretrained(self.model_name).to(dev).eval()
        self._dev = dev
        id2label = {int(k): v.lower() for k, v in self._mdl.config.id2label.items()}
        self._order = [next(i for i, v in id2label.items() if v.startswith(n)) for n in ("pos", "neg", "neu")]

    def _score_batch(self, texts: list[str]) -> np.ndarray:
        import torch
        enc = self._tok(texts, padding=True, truncation=True, max_length=self.max_length, return_tensors="pt")
        enc = {k: v.to(self._dev) for k, v in enc.items()}
        with torch.inference_mode():
            p = torch.softmax(self._mdl(**enc).logits.float(), dim=-1).cpu().numpy()
        return p[:, self._order]

    def score(self, texts: list[str]) -> pd.DataFrame:
        """Return DataFrame [p_pos, p_neg, p_neu] aligned with `texts` (cleaned before scoring)."""
        clean = [clean_text(t) for t in texts]
        keys = [_h(t) for t in clean]
        cache = pd.read_parquet(self.cache_path) if self.cache_path.exists() else pd.DataFrame(
            columns=["key", "p_pos", "p_neg", "p_neu"])
        known = set(cache["key"])
        todo = sorted({k: t for k, t in zip(keys, clean) if k not in known}.items(), key=lambda kv: len(kv[1]))
        if todo:
            if self._mdl is None:
                self._load()
            out = []
            for i in range(0, len(todo), self.batch_size):
                chunk = todo[i:i + self.batch_size]
                out.append(self._score_batch([t for _, t in chunk]))
            probs = np.concatenate(out)
            new = pd.DataFrame({"key": [k for k, _ in todo], "p_pos": probs[:, 0], "p_neg": probs[:, 1], "p_neu": probs[:, 2]})
            cache = pd.concat([cache, new], ignore_index=True).drop_duplicates("key")
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache.to_parquet(self.cache_path, index=False)
        m = cache.set_index("key").loc[keys, ["p_pos", "p_neg", "p_neu"]].astype(float)
        return m.reset_index(drop=True)


def score_docs(aligned: pd.DataFrame, scorer: FinBertScorer | None = None) -> pd.DataFrame:
    scorer = scorer or FinBertScorer()
    probs = scorer.score(aligned["text"].tolist())
    out = aligned.reset_index(drop=True).copy()
    out[["p_pos", "p_neg", "p_neu"]] = probs.values
    s = out[["p_pos", "p_neg", "p_neu"]].sum(1)
    out[["p_pos", "p_neg", "p_neu"]] = out[["p_pos", "p_neg", "p_neu"]].div(s, axis=0)
    out["sentiment"] = (out["p_pos"] - out["p_neg"]).clip(-1, 1)
    return validate(out, SCORED_DOCS)
