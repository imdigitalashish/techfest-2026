"""C3 text scorer v1 — MiniLM sentence embeddings + logistic-regression sentiment head.

Encoder: sentence-transformers/all-MiniLM-L6-v2 (mean pooling, L2-normalised; already in the local HF cache).
Head: multinomial logistic regression trained on Twitter Financial News Sentiment (HF zeroshot/, MIT;
labels 0 bearish / 1 bullish / 2 neutral). Labels are sentiment, not returns, so the head cannot leak
2014-2016 outcomes. `label_noise` flips that fraction of training labels uniformly at random (noisy-label
stretch). Embeddings are cached by text hash in .cache/emb_minilm.parquet.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from architecture.contracts.contracts import SCORED_DOCS, validate
from components.text_scorer.finbert import clean_text

ENCODER = "sentence-transformers/all-MiniLM-L6-v2"


class MiniLMEncoder:
    def __init__(self, cache_dir: str | Path = ".cache", batch_size: int = 256, device: str | None = None):
        self.cache_path = Path(cache_dir) / "emb_minilm.npz"
        self.batch_size, self._device, self._mdl = batch_size, device, None
        self._mem: dict[str, np.ndarray] = {}
        if self.cache_path.exists():
            z = np.load(self.cache_path, allow_pickle=False)
            self._mem = dict(zip(z["keys"].tolist(), z["emb"]))

    def _load(self):
        import torch
        from transformers import AutoModel, AutoTokenizer
        self._dev = self._device or ("mps" if torch.backends.mps.is_available() else "cpu")
        self._tok = AutoTokenizer.from_pretrained(ENCODER)
        self._mdl = AutoModel.from_pretrained(ENCODER).to(self._dev).eval()

    def _encode(self, texts: list[str]) -> np.ndarray:
        import torch
        enc = self._tok(texts, padding=True, truncation=True, max_length=64, return_tensors="pt").to(self._dev)
        with torch.inference_mode():
            h = self._mdl(**enc).last_hidden_state
            m = enc["attention_mask"].unsqueeze(-1).float()
            e = (h * m).sum(1) / m.sum(1).clamp(min=1e-9)
            e = torch.nn.functional.normalize(e, dim=-1)
        return e.float().cpu().numpy()

    def encode(self, texts: list[str]) -> np.ndarray:
        clean = [clean_text(t) for t in texts]
        keys = [hashlib.sha1(t.encode()).hexdigest() for t in clean]
        todo = sorted({k: t for k, t in zip(keys, clean) if k not in self._mem}.items(), key=lambda kv: len(kv[1]))
        if todo:
            if self._mdl is None:
                self._load()
            for i in range(0, len(todo), self.batch_size):
                chunk = todo[i:i + self.batch_size]
                for (k, _), e in zip(chunk, self._encode([t for _, t in chunk])):
                    self._mem[k] = e
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            np.savez(self.cache_path, keys=np.array(list(self._mem)), emb=np.stack(list(self._mem.values())))
        return np.stack([self._mem[k] for k in keys])


class MiniLMSentimentScorer:
    name = "minilm+lr"

    def __init__(self, train_csv: str | Path = ".data/tfns/sent_train.csv", label_noise: float = 0.0,
                 seed: int = 0, encoder: MiniLMEncoder | None = None):
        self.enc = encoder or MiniLMEncoder()
        tr = pd.read_csv(train_csv)
        y = tr["label"].to_numpy(int).copy()
        if label_noise > 0:
            rng = np.random.default_rng(seed)
            flip = rng.random(len(y)) < label_noise
            y[flip] = (y[flip] + rng.integers(1, 3, flip.sum())) % 3
        X = self.enc.encode(tr["text"].astype(str).tolist())
        self.clf = LogisticRegression(max_iter=2000, C=4.0, random_state=seed).fit(X, y)

    def proba(self, texts: list[str]) -> np.ndarray:
        """Columns: [bearish, bullish, neutral]."""
        p = self.clf.predict_proba(self.enc.encode(texts))
        return p[:, np.argsort(self.clf.classes_)]

    def score(self, texts: list[str]) -> pd.DataFrame:
        p = self.proba(texts)
        return pd.DataFrame({"p_pos": p[:, 1], "p_neg": p[:, 0], "p_neu": p[:, 2], "compound": p[:, 1] - p[:, 0]})


def score_docs_minilm(aligned: pd.DataFrame, scorer: MiniLMSentimentScorer | None = None) -> pd.DataFrame:
    scorer = scorer or MiniLMSentimentScorer()
    s = scorer.score(aligned["text"].tolist())
    out = aligned.reset_index(drop=True).copy()
    out[["p_pos", "p_neg", "p_neu"]] = s[["p_pos", "p_neg", "p_neu"]].values
    out["sentiment"] = s["compound"].clip(-1, 1).values
    return validate(out, SCORED_DOCS)
