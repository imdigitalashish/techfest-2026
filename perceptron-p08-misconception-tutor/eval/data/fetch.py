"""Fetch evaluation data into perceptron-p08-misconception-tutor/.data/ (gitignored).

Sources (opened 2026-10-04):
- Eedi Misconceptions Graph v1.0, CC BY 4.0, official Eedi release:
  https://huggingface.co/datasets/Eedi/Eedi-Misconceptions-Graph
- Kaggle "Eedi - Mining Misconceptions in Mathematics" (2024) training data, via the
  community Hugging Face mirror cdtmc/eedi-ir (IR format: queries, corpus of 2,587
  misconceptions, qrels with folds). The mirror has no stated licence; the data is
  Kaggle competition data, so we use it for non-commercial research evaluation only
  and do not redistribute it. Fidelity to the official Kaggle files is UNVERIFIED
  until checked against a Kaggle download (Needs from user: Kaggle account).

Usage: python -m eval.data.fetch
"""
from __future__ import annotations

import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = ROOT / ".data"

FILES = {
    "eedi_graph/misconception-map.csv": "https://huggingface.co/datasets/Eedi/Eedi-Misconceptions-Graph/resolve/main/data/misconception-map.csv",
    "eedi_graph/construct-map.csv": "https://huggingface.co/datasets/Eedi/Eedi-Misconceptions-Graph/resolve/main/data/construct-map.csv",
    "eedi2024/corpus.parquet": "https://huggingface.co/datasets/cdtmc/eedi-ir/resolve/main/corpus/train-00000-of-00001.parquet",
    "eedi2024/queries_w_rels.parquet": "https://huggingface.co/datasets/cdtmc/eedi-ir/resolve/main/queries_w_rels/train-00000-of-00001.parquet",
}


def fetch(force: bool = False) -> None:
    for rel, url in FILES.items():
        out = DATA / rel
        if out.exists() and not force:
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        print(f"fetching {url}", file=sys.stderr)
        urllib.request.urlretrieve(url, out)


if __name__ == "__main__":
    fetch(force="--force" in sys.argv)
