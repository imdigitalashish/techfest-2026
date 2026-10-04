"""Eval suite v1 — leakage-clean, shift-aware TechPort benchmark (ADR 002). Label: trl_current.

Fixes from the 08:30 review: (1) redaction — sentences that state a TRL are dropped, SBIR/STTR/Phase tokens removed;
(2) content-dedup grouping — union-find over title key, description hash, benefits hash, 200-char prefix;
(3) projects with DOI-linked papers (and their groups) are forced into TEST so the paired-paper condition is clean;
(4) a snapshot hash of (id, label) pairs pins the data version.
Outputs: .data/suite_v1/{train,test,papers}.jsonl + eval/splits/suite_v1_{test_ids.txt,meta.json}
Usage: python eval/build_suite_v1.py
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED, LABEL, TEST_PCT = 20261004, "trl_current", 20
SENT = re.compile(r"(?<=[.!?])\s+")
TRL_RX = re.compile(r"\bTRLs?\b|technology readiness|readiness level", re.I)
SBIR_RX = re.compile(r"\b(SBIR|STTR)\b|\bphase\s+(I{1,3}|[1-3])\b(?!\w)", re.I)


def redact(text: str) -> tuple[str, int]:
    sents = SENT.split(text)
    keep = [s for s in sents if not TRL_RX.search(s)]
    out = SBIR_RX.sub(" ", " ".join(keep))
    return re.sub(r"\s+", " ", out).strip(), len(sents) - len(keep)


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def title_key(t: str) -> str:  # same as baseline v0
    t = re.sub(r"(phase\s*(i{1,3}|[123])\b|sbir|sttr|\d{4})", " ", t.lower())
    return re.sub(r"[^a-z]+", " ", t).strip()[:60]


class DSU:
    def __init__(self):
        self.p = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        self.p[self.find(a)] = self.find(b)


def main():
    rows = [r for r in map(json.loads, (ROOT / ".data/techport/techport_trl.jsonl").open()) if r.get(LABEL)]
    snap = hashlib.sha256("\n".join(f"{r['id']}:{r[LABEL]}" for r in sorted(rows, key=lambda r: r["id"])).encode()).hexdigest()
    dsu = DSU()
    for r in rows:
        node = f"id:{r['id']}"
        keys = [f"t:{title_key(r['title'])}", f"d:{hashlib.md5(norm(r['description']).encode()).hexdigest()}",
                f"p:{norm(r['description'])[:200]}"]
        if len(norm(r["benefits"])) > 100:
            keys.append(f"b:{hashlib.md5(norm(r['benefits']).encode()).hexdigest()}")
        for k in keys:
            dsu.union(node, k)
    group = {r["id"]: dsu.find(f"id:{r['id']}") for r in rows}
    members = Counter(group.values())
    papers = [p for p in map(json.loads, (ROOT / ".data/openalex/linked_papers.jsonl").open())
              if len((p.get("abstract") or "").split()) >= 30]
    byid = {r["id"]: r for r in rows}
    papers = [p for p in papers if p["project_id"] in byid]
    forced = {group[p["project_id"]] for p in papers}
    # canonical group key = smallest member id (stable while the group is unchanged)
    gmin = {}
    for r in rows:
        g = group[r["id"]]
        gmin[g] = min(gmin.get(g, r["id"]), r["id"])
    def is_test(g):
        return g in forced or int(hashlib.sha1(f"{SEED}:{gmin[g]}".encode()).hexdigest(), 16) % 100 < TEST_PCT
    out = ROOT / ".data/suite_v1"; out.mkdir(parents=True, exist_ok=True)
    n_red, n_trl_docs = 0, 0
    with (out / "train.jsonl").open("w") as ftr, (out / "test.jsonl").open("w") as fte:
        for r in rows:
            text, dropped = redact(r["text"])
            n_red += dropped; n_trl_docs += dropped > 0
            rec = {"id": r["id"], "text": text, "label": r[LABEL], "source": "sbir" if r["program"] == "SBIR/STTR" else "internal",
                   "group": gmin[group[r["id"]]], "had_trl_statement": dropped > 0, "has_paper": group[r["id"]] in forced}
            (fte if is_test(group[r["id"]]) else ftr).write(json.dumps(rec) + "\n")
    with (out / "papers.jsonl").open("w") as f:
        for p in papers:
            text, _ = redact(p["title"] + ". " + p["abstract"])
            f.write(json.dumps({"project_id": p["project_id"], "doi": p["doi"], "text": text, "label": byid[p["project_id"]][LABEL]}) + "\n")
    tr = [json.loads(l) for l in (out / "train.jsonl").open()]; te = [json.loads(l) for l in (out / "test.jsonl").open()]
    assert not ({r["group"] for r in tr} & {r["group"] for r in te}), "group leak"
    meta = {"snapshot_sha256": snap, "label": LABEL, "seed": SEED, "n_rows": len(rows), "n_groups": len(members),
            "n_multi_member_groups": sum(c > 1 for c in members.values()), "n_train": len(tr), "n_test": len(te),
            "n_papers": len(papers), "n_paper_projects": len({p['project_id'] for p in papers}),
            "trl_sentences_dropped": n_red, "docs_with_trl_statement": n_trl_docs,
            "test_by_source": dict(Counter(r["source"] for r in te)), "train_by_source": dict(Counter(r["source"] for r in tr)),
            "test_label_dist": dict(sorted(Counter(r["label"] for r in te).items()))}
    (ROOT / "eval/splits/suite_v1_test_ids.txt").write_text("\n".join(str(r["id"]) for r in sorted(te, key=lambda r: r["id"])) + "\n")
    (ROOT / "eval/splits/suite_v1_meta.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
