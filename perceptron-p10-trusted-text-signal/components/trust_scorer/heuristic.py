"""C4 trust scorer — per-document credibility weight in [0, 1] from that document's OWN metadata.

Trust must be deletion-stable for the certificate (C10): removing or adding other documents must not
change a document's trust. So `trust` uses only per-document fields (followers, account age, verified,
cashtag spam). The copy-paste cluster size `dup_cluster` depends on the whole ticker-day; it is kept as
a detection signal (C4 isolated metric) but is NOT used in `trust` or in any certified feature.
Isolated metric: AUROC of (1 - trust) and of dup_cluster for separating injected from real documents.
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

from architecture.contracts.contracts import TRUSTED_DOCS, validate

_NORM = re.compile(r"https?://\S+|@\w+|[^a-z$ ]")


def _norm(t: str) -> str:
    return " ".join(_NORM.sub(" ", t.lower()).replace("rt ", " ").split())


def trust_of(followers, age_days, verified, n_cashtags) -> np.ndarray:
    f_follow = np.clip(np.log1p(np.asarray(followers, float)) / np.log(10_000), 0, 1)
    f_age = np.clip(np.asarray(age_days, float) / 365.0, 0, 1)
    f_ver = np.asarray(verified, float)
    p_spam = (np.asarray(n_cashtags) >= 4).astype(float)
    return np.clip(0.4 * f_follow + 0.4 * f_age + 0.2 * f_ver - 0.2 * p_spam + 0.1, 0.05, 1.0)


def score_trust(scored: pd.DataFrame) -> pd.DataFrame:
    d = scored.copy()
    key = d["text"].map(_norm)
    d["dup_cluster"] = d.groupby([d["ticker"], d["trade_date"], key])["doc_id"].transform("count").astype(int)
    d["trust"] = trust_of(d["user_followers"], d["user_age_days"], d["user_verified"], d["n_cashtags"])
    return validate(d, TRUSTED_DOCS)
