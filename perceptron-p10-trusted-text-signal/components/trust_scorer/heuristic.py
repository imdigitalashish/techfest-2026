"""C4 trust scorer — per-document credibility weight in [0, 1] from account metadata + coordination cues.

Baseline heuristic (transparent, no training): older, followed, verified accounts score higher;
near-duplicate copies within a ticker-day (copypasta / coordinated posting) and multi-cashtag
spam blasts score lower. Isolated metric: AUROC of (1 - trust) for separating injected from real
documents under a stated attacker model (weak bot vs metadata-mimicking attacker).
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

from architecture.contracts.contracts import TRUSTED_DOCS, validate

_NORM = re.compile(r"https?://\S+|@\w+|[^a-z$ ]")


def _norm(t: str) -> str:
    return " ".join(_NORM.sub(" ", t.lower()).replace("rt ", " ").split())


def score_trust(scored: pd.DataFrame) -> pd.DataFrame:
    d = scored.copy()
    key = d["text"].map(_norm)
    d["dup_cluster"] = d.groupby([d["ticker"], d["trade_date"], key])["doc_id"].transform("count").astype(int)
    f_follow = np.clip(np.log1p(d["user_followers"]) / np.log(10_000), 0, 1)
    f_age = np.clip(d["user_age_days"] / 365.0, 0, 1)
    f_ver = d["user_verified"].astype(float)
    p_dup = np.clip(np.log2(d["dup_cluster"].clip(lower=1)) / 4.0, 0, 1)
    p_spam = (d["n_cashtags"] >= 4).astype(float)
    d["trust"] = np.clip(0.4 * f_follow + 0.4 * f_age + 0.2 * f_ver - 0.3 * p_dup - 0.2 * p_spam + 0.1, 0.05, 1.0)
    return validate(d, TRUSTED_DOCS)
