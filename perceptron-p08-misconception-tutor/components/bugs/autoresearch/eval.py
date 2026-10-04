"""FROZEN evaluator for the C3 autoresearch loop. The loop must never edit this file.

Prints one scalar line `METRIC reproduction_dev=<float>` plus guard metrics.
Data: Kaggle Eedi 2024 distractors (mirror cdtmc/eedi-ir, fetched by `python -m eval.data.fetch`) whose
label is one of the Eedi misconceptions linked to our five pack categories (n=129). Split by question
hash: dev (optimised) / holdout (only for the lead's periodic check). Guards (a change is rejected if
violated): wrong_attribution must stay 0.0; false_claim_rate on other-labelled distractors <= 0.03.
Run from the project folder: .venv/bin/python components/bugs/autoresearch/eval.py
"""
from __future__ import annotations

import hashlib
import pathlib
import re
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from components.bugs.eedi_parse import executable_match  # noqa: E402
from components.bugs.school_math import CODES, EEDI_LINKS  # noqa: E402


def split_query(q: str):
    m = re.match(r"### Question:(.*?)### Correct:(.*?)### Incorrect:(.*)", q, re.S)
    return tuple(x.strip() for x in m.groups()) if m else (q, "", "")


def main() -> None:
    df = pd.read_parquet(ROOT / ".data/eedi2024/queries_w_rels.parquet")
    link = {i: cd for cd in CODES for i in EEDI_LINKS[cd]["kaggle2024"]}
    df["code"] = df.mid.map(link)
    df["question"] = df["query"].map(lambda s: split_query(s)[0])
    df["dev"] = df["question"].map(lambda s: int(hashlib.md5(s.encode()).hexdigest(), 16) % 2 == 0)
    stats = {}
    for split in ("dev", "holdout"):
        pos = df[df.code.notna() & (df.dev == (split == "dev"))]
        rep = wrong = parsed = 0
        for qtext, code in zip(pos["query"], pos.code):
            p, _, matched = executable_match(*split_query(qtext))
            parsed += p
            rep += code in matched
            wrong += bool(matched) and code not in matched
        stats[f"reproduction_{split}"] = rep / len(pos)
        stats[f"parsed_{split}"] = parsed / len(pos)
        stats[f"wrong_attribution_{split}"] = wrong / len(pos)
        stats[f"n_{split}"] = len(pos)
    neg = df[df.code.isna()]
    claims = checked = 0
    for qtext in neg["query"]:
        p, key_ok, matched = executable_match(*split_query(qtext))
        if p and key_ok:
            checked += 1
            claims += bool(matched)
    stats["false_claim_rate"] = claims / max(1, checked)
    stats["negatives_checked"] = checked
    print(f"METRIC reproduction_dev={stats['reproduction_dev']:.4f}")
    print(" ".join(f"{k}={v:.4f}" if isinstance(v, float) else f"{k}={v}" for k, v in stats.items()))


if __name__ == "__main__":
    main()
