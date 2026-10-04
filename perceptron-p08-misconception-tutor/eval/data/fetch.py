"""Fetch evaluation data into perceptron-p08-misconception-tutor/.data/ (gitignored), pinned and checksummed.

Sources (opened 2026-10-04):
- Eedi Misconceptions Graph v1.0, CC BY 4.0, official Eedi release:
  https://huggingface.co/datasets/Eedi/Eedi-Misconceptions-Graph (pinned revision below)
- Kaggle "Eedi - Mining Misconceptions in Mathematics" (2024) training data, via the community Hugging Face
  mirror cdtmc/eedi-ir (IR format: queries, corpus of 2,587 misconceptions, qrels with folds). The mirror has
  no stated licence. The Kaggle rules (https://www.kaggle.com/competitions/eedi-mining-misconceptions-in-mathematics/rules,
  opened 2026-10-04) make the data CC BY-NC 4.0 (non-commercial only), and §7.B forbids participants to publish or
  redistribute it. We use it only for non-commercial research evaluation, keep it in gitignored .data/, and commit
  no item text, only derived outcomes (item ids, codes, aggregates). Fidelity to the official Kaggle files is UNVERIFIED until checked against a
  Kaggle download (Needs from user: Kaggle account).
Revisions and SHA-256 checksums were pinned on 4 Oct 2026 (review fix): the files used for every committed result
match these hashes; a stale or changed local file is rejected.

Usage: python -m eval.data.fetch [--force]
"""
from __future__ import annotations

import hashlib
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = ROOT / ".data"

EEDI_IR = "ccf31188eceb99e121a65aa82c5587334062cd8e"       # cdtmc/eedi-ir, lastModified 2024-11-27
EEDI_GRAPH = "2ae0839debf73c0ce7dd6578d8ea8b99e7be8631"    # Eedi/Eedi-Misconceptions-Graph, lastModified 2026-09-16

FILES = {
    "eedi_graph/misconception-map.csv": (
        f"https://huggingface.co/datasets/Eedi/Eedi-Misconceptions-Graph/resolve/{EEDI_GRAPH}/data/misconception-map.csv",
        "3937e12b96ba2659ab16f060edfffeb6f35a1cce5fb60caedf6955a1b6fed0c2"),
    "eedi_graph/construct-map.csv": (
        f"https://huggingface.co/datasets/Eedi/Eedi-Misconceptions-Graph/resolve/{EEDI_GRAPH}/data/construct-map.csv",
        "45a0fb21687f9b13cc59bb9aa011a39347637e304a8c239ee6d447b5bd77051b"),
    "eedi2024/corpus.parquet": (
        f"https://huggingface.co/datasets/cdtmc/eedi-ir/resolve/{EEDI_IR}/corpus/train-00000-of-00001.parquet",
        "7579e45c59d85a4202b634db17a5d5c869a00aaca57212e66ebf494cf7221891"),
    "eedi2024/queries_w_rels.parquet": (
        f"https://huggingface.co/datasets/cdtmc/eedi-ir/resolve/{EEDI_IR}/queries_w_rels/train-00000-of-00001.parquet",
        "103da69cd0ac1e01fdaac70d90b265bcc04f29ebf5fbac90872685fedf42b6e9"),
}


def sha256(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(force: bool = False) -> None:
    for rel, (url, digest) in FILES.items():
        out = DATA / rel
        if out.exists() and not force and sha256(out) == digest:
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        print(f"fetching {url}", file=sys.stderr)
        urllib.request.urlretrieve(url, out)
        got = sha256(out)
        if got != digest:
            raise RuntimeError(f"checksum mismatch for {rel}: {got} != {digest}")


if __name__ == "__main__":
    fetch(force="--force" in sys.argv)
