"""Build the natural-text haystack used by the recall tasks.

Source: WikiText-103 raw v1 (validation + test splits), Hugging Face dataset `wikitext`
(https://huggingface.co/datasets/wikitext, CC BY-SA 3.0), pinned revision below.
Output: .data/haystack.txt (gitignored), one cleaned paragraph per line.

Usage:  python3 eval/fetch_haystack.py   (needs pyarrow + huggingface_hub; uses the HF cache)
"""
from __future__ import annotations

import re
from pathlib import Path

import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".data" / "haystack.txt"
REVISION = "b08601e04326c79dfdd32d625aee71d232d685c3"
FILES = [
    "wikitext-103-raw-v1/validation-00000-of-00001.parquet",
    "wikitext-103-raw-v1/test-00000-of-00001.parquet",
]


def clean(line: str) -> str:
    line = line.strip()
    if not line or line.startswith("="):  # section headings such as " = = Title = = "
        return ""
    for a, b in ((" @-@ ", "-"), (" @,@ ", ","), (" @.@ ", ".")):
        line = line.replace(a, b)
    line = re.sub(r"\s+([,.;:!?)'])", r"\1", line)
    line = re.sub(r"([(])\s+", r"\1", line)
    line = line.replace(" n't", "n't").replace(" 's", "'s")
    return re.sub(r"\s{2,}", " ", line)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    paras = []
    for f in FILES:
        path = hf_hub_download("wikitext", f, repo_type="dataset", revision=REVISION)
        for line in pq.read_table(path).column("text").to_pylist():
            c = clean(line)
            if len(c) > 80:
                paras.append(c)
    OUT.write_text("\n".join(paras), encoding="utf-8")
    print(f"wrote {OUT} paragraphs={len(paras)} chars={sum(map(len, paras))}")


if __name__ == "__main__":
    main()
