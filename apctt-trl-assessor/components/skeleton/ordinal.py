"""C4 Ordinal TRL model v0 (numpy threshold-ridge): text -> TRLDistribution.

Same features as eval/baseline_numpy.py (hashed uni+bigram log-TF*IDF, L2). Trained on the TRAIN part of the
frozen TechPort split only, so held-out examples stay honest.
"""
from __future__ import annotations

import json
import re
import zlib
from pathlib import Path

import numpy as np

K = 9
TOK = re.compile(r"[a-z][a-z0-9\-]{1,30}")
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = ROOT / ".data" / "models" / "thr_ridge_v0_trl_current.npz"


def featurize(texts, D):
    X = np.zeros((len(texts), D), dtype=np.float32)
    for i, t in enumerate(texts):
        w = TOK.findall(t.lower())
        for tok in w + [a + " " + b for a, b in zip(w, w[1:])]:
            X[i, zlib.crc32(tok.encode()) % D] += 1.0
    return np.log1p(X)


def train(label: str = "trl_current", D: int = 4096, alpha: float = 1.0, out: Path = DEFAULT_MODEL) -> Path:
    rows = [json.loads(l) for l in (ROOT / ".data" / "techport" / "techport_trl.jsonl").open()]
    test_ids = set(int(x) for x in (ROOT / "eval" / "splits" / f"techport_v0_{label}_test_ids.txt").read_text().split())
    tr = [r for r in rows if r.get(label) and r["id"] not in test_ids]
    y = np.array([r[label] for r in tr], dtype=np.float32)
    X = featurize([r["text"] for r in tr], D)
    idf = (np.log((1 + len(tr)) / (1 + (X > 0).sum(0))) + 1).astype(np.float32)
    X *= idf
    X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-9
    T = np.column_stack([(y > k).astype(np.float32) for k in range(1, K)])
    mu, xm = T.mean(0), X.mean(0)
    Xc = X - xm
    W = np.linalg.solve(Xc.T @ Xc + alpha * np.eye(D, dtype=np.float32), Xc.T @ (T - mu))
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, W=W, mu=mu, xm=xm, idf=idf, D=D, label=label, n_train=len(tr))
    return out


class Model:
    def __init__(self, path: Path = DEFAULT_MODEL):
        z = np.load(path)
        self.W, self.mu, self.xm, self.idf, self.D = z["W"], z["mu"], z["xm"], z["idf"], int(z["D"])
        self.model_id = f"thr_ridge_v0:{z['label']}:n{int(z['n_train'])}:D{self.D}"

    def predict(self, text: str) -> dict:
        x = featurize([text], self.D) * self.idf
        x /= np.linalg.norm(x, axis=1, keepdims=True) + 1e-9
        gt = np.clip((x - self.xm) @ self.W + self.mu, 0, 1)[0]
        gt = np.minimum.accumulate(gt)
        cdf = np.concatenate([[1.0], gt, [0.0]])
        p = np.clip(cdf[:-1] - cdf[1:], 0, 1) + 1e-6
        p = p / p.sum()
        p_gt = 1 - np.cumsum(p)[:-1]  # recomputed from p so the two are mutually consistent
        return {"p": [float(v) for v in p], "p_gt": [float(min(max(v, 0.0), 1.0)) for v in p_gt], "model_id": self.model_id}
