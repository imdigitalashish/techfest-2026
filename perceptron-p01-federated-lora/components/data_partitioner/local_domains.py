"""C1 Data partitioner: per-domain token blocks built from real text already on this machine.

One domain per device gives a pathological non-IID split (domain skew); the device profiles
add quantity skew. Every domain is real text, none of it synthetic:

  wiki      WikiText-103 (local HF cache): train split → train pool, test split → eval pool
  pycode    Python source of installed packages (site-packages)
  cheaders  C/C++ headers shipped with PyTorch (torch/include)
  readmes   package READMEs (dist-info METADATA long descriptions, *.md)
  manpages  raw groff man pages (/usr/share/man/man1, macOS)

Non-wiki domains split train/eval by file (sha1 of the path), so no document crosses the split.
Contents depend on the pinned package versions in requirements.txt, which keeps them reproducible.
Why local text: during the overnight build PyPI/HF downloads ran at ~0.3–0.6 KB/s (see the thought
node), so standard benchmarks (FlowerTune finance, Dolly-15k) are the next step, not this one.
Tokenised blocks are cached in .data/ (gitignored).
"""
from __future__ import annotations

import glob
import hashlib
import os
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / ".data"
SITE = Path(sys.prefix) / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
WIKI_GLOB = str(Path.home() / ".cache/huggingface/hub/datasets--wikitext/snapshots/*/wikitext-103-raw-v1")

DOMAINS = ["wiki", "pycode", "cheaders", "readmes", "manpages"]
MAX_FILES = 3000
MAX_CHARS_PER_FILE = 12000


def _is_eval(path: str) -> bool:
    return int(hashlib.sha1(path.encode()).hexdigest(), 16) % 10 == 0


def _read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(MAX_CHARS_PER_FILE)
    except OSError:
        return ""


def _sorted_files(patterns: list[str]) -> list[str]:
    files: set[str] = set()
    for pat in patterns:
        files.update(glob.glob(pat, recursive=True))
    # deterministic, well-mixed order independent of filesystem order
    return sorted(files, key=lambda p: hashlib.sha1(p.encode()).hexdigest())[:MAX_FILES]


def _file_docs(domain: str) -> tuple[list[str], list[str]]:
    s = str(SITE)
    patterns = {
        "pycode": [f"{s}/transformers/**/*.py", f"{s}/torch/**/*.py", f"{s}/pandas/**/*.py", f"{s}/scipy/**/*.py"],
        "cheaders": [f"{s}/torch/include/**/*.h"],
        "readmes": [f"{s}/*.dist-info/METADATA", f"{s}/**/*.md"],
        "manpages": ["/usr/share/man/man1/*.1"],
    }[domain]
    train, ev = [], []
    for p in _sorted_files(patterns):
        txt = _read(p)
        if len(txt) < 200:
            continue
        (ev if _is_eval(p) else train).append(txt)
    return train, ev


def _wiki_docs() -> tuple[list[str], list[str]]:
    import pandas as pd

    snaps = sorted(glob.glob(WIKI_GLOB))
    if not snaps:
        raise FileNotFoundError("WikiText-103 not in the HF cache; run scripts/fetch_data.sh")
    d = Path(snaps[-1])
    train_rows = pd.read_parquet(d / "train-00000-of-00002.parquet")["text"].tolist()[:60000]
    test_rows = pd.read_parquet(d / "test-00000-of-00001.parquet")["text"].tolist()

    def group(rows: list[str], n: int = 40) -> list[str]:
        return ["".join(rows[i : i + n]) for i in range(0, len(rows), n)]

    return group(train_rows), group(test_rows)


def _blocks(tokenizer, docs: list[str], seq_len: int, max_blocks: int) -> torch.Tensor:
    ids: list[int] = []
    eos = tokenizer.eos_token_id
    need = max_blocks * seq_len
    for doc in docs:
        ids.extend(tokenizer(doc, add_special_tokens=False)["input_ids"])
        ids.append(eos)
        if len(ids) >= need:
            break
    n = min(len(ids) // seq_len, max_blocks)
    return torch.tensor(ids[: n * seq_len], dtype=torch.long).view(n, seq_len)


def build_domain_blocks(tokenizer, domain: str, seq_len: int = 128, max_train_blocks: int = 2400,
                        n_eval_blocks: int = 48, model_tag: str = "model") -> tuple[torch.Tensor, torch.Tensor]:
    """Return (train_blocks [N, T], eval_blocks [M, T]) for one domain, cached in .data/."""
    DATA_DIR.mkdir(exist_ok=True)
    cache = DATA_DIR / f"blocks_{domain}_{model_tag}_T{seq_len}_N{max_train_blocks}_E{n_eval_blocks}.pt"
    if cache.exists():
        d = torch.load(cache)
        return d["train"], d["eval"]
    train_docs, eval_docs = _wiki_docs() if domain == "wiki" else _file_docs(domain)
    tr = _blocks(tokenizer, train_docs, seq_len, max_train_blocks)
    ev = _blocks(tokenizer, eval_docs, seq_len, n_eval_blocks)
    if tr.shape[0] < 300 or ev.shape[0] < n_eval_blocks:
        raise RuntimeError(f"domain {domain}: too little text ({tr.shape[0]} train / {ev.shape[0]} eval blocks)")
    torch.save({"train": tr, "eval": ev}, cache)
    return tr, ev


if __name__ == "__main__":
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained("HuggingFaceTB/SmolLM2-135M", local_files_only=True)
    for dom in DOMAINS:
        tr, ev = build_domain_blocks(tok, dom, model_tag="smollm2-135m")
        print(f"{dom:9s} train={tuple(tr.shape)} eval={tuple(ev.shape)}")
