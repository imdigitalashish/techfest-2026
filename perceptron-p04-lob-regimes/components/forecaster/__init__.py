"""C5 Forecaster heads: standardised features -> P(mid up over horizon).

LogisticHead is deliberately simple (d+1 weights): microsecond inference, closed-form
online SGD updates, and an L2 pull towards a prior weight vector so refits on small
post-shift windows stay stable. Stronger heads (GBDT, small DeepLOB-style nets) plug in
behind the same predict / update / refit interface.
"""
from __future__ import annotations

import numpy as np
from sklearn.linear_model import LogisticRegression


def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))


class LogisticHead:
    def __init__(self, d: int, name: str = "head"):
        self.name = name
        self.w = np.zeros(d)
        self.b = 0.0

    def copy(self, name: str | None = None) -> "LogisticHead":
        h = LogisticHead(len(self.w), name or self.name)
        h.w, h.b = self.w.copy(), self.b
        return h

    def fit(self, Z: np.ndarray, y: np.ndarray, C: float = 1.0) -> "LogisticHead":
        m = ~np.isnan(y)
        lr = LogisticRegression(C=C, max_iter=500)
        lr.fit(Z[m], y[m].astype(int))
        self.w, self.b = lr.coef_[0].copy(), float(lr.intercept_[0])
        return self

    def refit_towards(self, Z: np.ndarray, y: np.ndarray, prior: "LogisticHead", lam: float = 1.0,
                      iters: int = 60, lr: float = 0.5) -> "LogisticHead":
        """MAP refit with Gaussian prior centred on `prior` (full-batch gradient descent)."""
        m = ~np.isnan(y)
        Z, y = Z[m], y[m]
        if len(y) < 50:
            return self
        w, b = prior.w.copy(), prior.b
        n = len(y)
        for _ in range(iters):
            p = _sigmoid(Z @ w + b)
            g = p - y
            w -= lr * (Z.T @ g / n + lam / n * (w - prior.w))
            b -= lr * g.mean()
        self.w, self.b = w, b
        return self

    def predict(self, z: np.ndarray) -> float:
        return float(_sigmoid(z @ self.w + self.b))

    def predict_batch(self, Z: np.ndarray) -> np.ndarray:
        return _sigmoid(Z @ self.w + self.b)

    def sgd_update(self, z: np.ndarray, y: float, lr: float, l2: float = 0.0,
                   prior: "LogisticHead | None" = None) -> None:
        p = _sigmoid(z @ self.w + self.b)
        g = p - y
        pull = (self.w - prior.w) if prior is not None else self.w
        self.w -= lr * (g * z + l2 * pull)
        self.b -= lr * g
