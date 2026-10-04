"""C3 text scorer (overnight baseline) — VADER social-media sentiment + a small finance lexicon.

VADER: Hutto & Gilbert (ICWSM 2014), rule-based, built for social-media text; package `vaderSentiment`.
The finance additions below are hand-set (labelled heuristic). FinBERT (finbert.py) is the planned
upgrade once its ~440 MB weights can be fetched; both satisfy the SCORED_DOCS contract.
"""
from __future__ import annotations

import pandas as pd

from architecture.contracts.contracts import SCORED_DOCS, validate
from components.text_scorer.finbert import clean_text

FIN_LEXICON = {  # VADER valence scale is roughly [-4, 4]
    "bullish": 2.5, "bull": 1.5, "long": 1.0, "calls": 1.2, "buy": 1.5, "buying": 1.5, "upgrade": 2.0,
    "upgraded": 2.0, "beat": 1.8, "beats": 1.8, "outperform": 2.0, "rally": 1.8, "breakout": 1.8, "moon": 2.0,
    "soar": 2.2, "soars": 2.2, "surge": 2.0, "surges": 2.0, "record": 1.0, "higher": 1.0, "gains": 1.5,
    "bearish": -2.5, "bear": -1.5, "short": -1.0, "puts": -1.2, "sell": -1.5, "selling": -1.5, "downgrade": -2.0,
    "downgraded": -2.0, "miss": -1.8, "misses": -1.8, "underperform": -2.0, "plunge": -2.5, "plunges": -2.5,
    "crash": -2.8, "dump": -2.0, "lower": -1.0, "losses": -1.5, "lawsuit": -1.8, "recall": -1.5, "fraud": -3.0,
}


class VaderScorer:
    name = "vader+fin"

    def __init__(self):
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        self._a = SentimentIntensityAnalyzer()
        self._a.lexicon.update(FIN_LEXICON)

    def score(self, texts: list[str]) -> pd.DataFrame:
        rows = [self._a.polarity_scores(clean_text(t)) for t in texts]
        return pd.DataFrame({"p_pos": [r["pos"] for r in rows], "p_neg": [r["neg"] for r in rows],
                             "p_neu": [r["neu"] for r in rows], "compound": [r["compound"] for r in rows]})


def score_docs_vader(aligned: pd.DataFrame, scorer: VaderScorer | None = None) -> pd.DataFrame:
    scorer = scorer or VaderScorer()
    s = scorer.score(aligned["text"].tolist())
    out = aligned.reset_index(drop=True).copy()
    p = s[["p_pos", "p_neg", "p_neu"]].copy()
    tot = p.sum(1).replace(0, 1.0)
    p = p.div(tot, axis=0)
    p.loc[s[["p_pos", "p_neg", "p_neu"]].sum(1) == 0, ["p_pos", "p_neg", "p_neu"]] = [0.0, 0.0, 1.0]
    out[["p_pos", "p_neg", "p_neu"]] = p.values
    out["sentiment"] = s["compound"].clip(-1, 1).values
    return validate(out, SCORED_DOCS)
