"""The ONLY file the ratchet edits. CONFIG selects/composes rules from rules.py."""
from __future__ import annotations

import numpy as np

from components.decision.autoresearch import rules as R

CONFIG = {"rule": "threshold", "by": ["pair_id", "fee_bps", "delta_ms"]}


def fit(train):
    c = CONFIG
    if c["rule"] == "threshold":
        return R.fit_threshold(train, c["by"])
    if c["rule"] == "ev":
        return R.fit_ev(train, c["strata"], c.get("lam_mult", 1.0))
    if c["rule"] == "gbm_reg":
        return R.fit_gbm_reg(train, iters=c.get("iters", 200))
    if c["rule"] == "gbm_clf":
        return R.fit_gbm_clf(train, iters=c.get("iters", 200))
    if c["rule"] == "and":
        return (R.fit_threshold(train, c["by"]), R.fit_ev(train, c["strata"], c.get("lam_mult", 1.0)))
    raise ValueError(c)


def act(model, rows):
    c = CONFIG
    if c["rule"] == "threshold":
        return R.act_threshold(model, rows)
    if c["rule"] == "ev":
        return R.act_ev(model, rows)
    if c["rule"] == "gbm_reg":
        return R.act_gbm_reg(model, rows, c.get("margin", 0.0))
    if c["rule"] == "gbm_clf":
        return R.act_gbm_clf(model, rows)
    if c["rule"] == "and":
        return np.logical_and(R.act_threshold(model[0], rows), R.act_ev(model[1], rows))
    raise ValueError(c)
