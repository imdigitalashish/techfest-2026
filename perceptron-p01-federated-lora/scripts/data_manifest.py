#!/usr/bin/env python3
"""Data manifest + leakage check for the local-text domains (code review 2026-10-04, item 8). CPU only.

Re-derives, with the same code path as components/data_partitioner/local_domains.py, exactly which documents fill
each domain's train and eval token blocks; records sha1 of each document's content (as read) and a digest of the
resulting blocks; checks exact-content duplicates (a) between train and eval within a domain, (b) across domains.

Usage: python scripts/data_manifest.py   → eval/results/data_manifest.json (+ printed summary)
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("HF_HUB_OFFLINE", "1")

import torch  # noqa: E402
from transformers import AutoTokenizer  # noqa: E402

from components.data_partitioner import local_domains as ld  # noqa: E402

T, N_TRAIN, N_EVAL = 128, 2400, 48


def used_docs(tok, docs: list[str], max_blocks: int) -> tuple[list[str], torch.Tensor]:
    """Mirror of local_domains._blocks that also returns which documents were consumed."""
    ids, used, need = [], [], max_blocks * T
    for doc in docs:
        ids.extend(tok(doc, add_special_tokens=False)["input_ids"])
        ids.append(tok.eos_token_id)
        used.append(doc)
        if len(ids) >= need:
            break
    n = min(len(ids) // T, max_blocks)
    return used, torch.tensor(ids[: n * T], dtype=torch.long).view(n, T)


def sha(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", "ignore")).hexdigest()


def main() -> None:
    tok = AutoTokenizer.from_pretrained("HuggingFaceTB/SmolLM2-135M", local_files_only=True)
    man, hashes = {}, {}
    for dom in ld.DOMAINS:
        train_docs, eval_docs = ld._wiki_docs() if dom == "wiki" else ld._file_docs(dom)
        tr_used, tr_blocks = used_docs(tok, train_docs, N_TRAIN)
        ev_used, ev_blocks = used_docs(tok, eval_docs, N_EVAL)
        cached = ld.DATA_DIR / f"blocks_{dom}_smollm2-135m_T{T}_N{N_TRAIN}_E{N_EVAL}.pt"
        match = None
        if cached.exists():
            c = torch.load(cached)
            match = bool(torch.equal(c["train"], tr_blocks) and torch.equal(c["eval"], ev_blocks))
        tr_h, ev_h = [sha(d) for d in tr_used], [sha(d) for d in ev_used]
        hashes[dom] = (set(tr_h), set(ev_h))
        man[dom] = {
            "train_docs_used": len(tr_used), "eval_docs_used": len(ev_used),
            "train_blocks": int(tr_blocks.shape[0]), "eval_blocks": int(ev_blocks.shape[0]),
            "eval_tokens": int(ev_blocks.numel()),
            "train_eval_exact_duplicates": len(set(tr_h) & set(ev_h)),
            "blocks_sha1": hashlib.sha1(tr_blocks.numpy().tobytes() + ev_blocks.numpy().tobytes()).hexdigest()[:12],
            "matches_cached_blocks": match,
            "eval_doc_sha1": ev_h,
        }
    cross = {}
    doms = list(hashes)
    for i, a in enumerate(doms):
        for b in doms[i + 1:]:
            ua = hashes[a][0] | hashes[a][1]
            ub = hashes[b][0] | hashes[b][1]
            cross[f"{a}~{b}"] = len(ua & ub)
    out = {"tokenizer": "HuggingFaceTB/SmolLM2-135M", "block_tokens": T, "domains": man,
           "cross_domain_exact_duplicates": cross,
           "note": "non-wiki split = sha1(absolute path) % 10 == 0 → eval; this manifest pins the exact documents used"}
    (ROOT / "eval" / "results" / "data_manifest.json").write_text(json.dumps(out, indent=1) + "\n")
    for d, m in man.items():
        print(f"{d:9s} train docs {m['train_docs_used']:5d} · eval docs {m['eval_docs_used']:4d} · eval tokens "
              f"{m['eval_tokens']} · train∩eval dup {m['train_eval_exact_duplicates']} · cache match {m['matches_cached_blocks']}")
    print("cross-domain duplicates:", {k: v for k, v in cross.items() if v} or "none")


if __name__ == "__main__":
    main()
