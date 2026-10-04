"""C4 entrant (edited by the autoresearch loop; evaluated by autoresearch/eval.py, which is frozen).

E0 baseline: hashed uni+bigram log-TF*IDF (D=4096, same as the skeleton) + ridge on the TRL value, rounded.
"""
from __future__ import annotations

import numpy as np

from components.skeleton.ordinal import featurize

D, ALPHA = 4096, 1.0


def _x(state, texts):
    X = featurize(texts, D) * state["idf"]
    X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-9
    return X - state["xm"]


def fit(texts, y):
    X = featurize(texts, D)
    idf = (np.log((1 + len(texts)) / (1 + (X > 0).sum(0))) + 1).astype(np.float32)
    X *= idf; X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-9
    xm = X.mean(0); Xc = X - xm; ym = float(y.mean())
    w = np.linalg.solve(Xc.T @ Xc + ALPHA * np.eye(D, dtype=np.float32), Xc.T @ (y - ym).astype(np.float32))
    return {"idf": idf, "xm": xm, "w": w, "ym": ym}


def predict(state, texts):
    return np.clip(np.rint(_x(state, texts) @ state["w"] + state["ym"]), 1, 9).astype(int)
