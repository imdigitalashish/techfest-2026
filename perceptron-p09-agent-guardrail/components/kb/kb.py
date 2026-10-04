"""Reference knowledge base: the verifiable source every proposed action is checked against.

Contract: read-only queries; every answer carries a locator so the guard can cite it as Evidence.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from rank_bm25 import BM25Okapi

DATA = Path(__file__).parent / "data"
_TOKEN = re.compile(r"[a-z0-9&.%₹]+")


def _tok(s: str) -> list[str]:
    return _TOKEN.findall(s.lower())


@dataclass(frozen=True)
class Clause:
    clause_id: str
    text: str


class ReferenceKB:
    def __init__(self, data_dir: Path = DATA):
        self.dir = data_dir
        self.instruments = {r["symbol"]: r for r in self._load("instruments.json")["instruments"]}
        accts = self._load("accounts.json")
        self.accounts = {a["account_id"]: a for a in accts["accounts"]}
        self.principals = {p["user_id"]: p for p in accts["principals"]}
        self.restricted = {r["symbol"]: r for r in self._load("restricted.json")["restricted"]}
        self.limits = {k: v for k, v in self._load("limits.json").items() if not k.startswith("_")}
        self.policy_text = (self.dir / "policies.md").read_text()
        self.clauses = {
            m.group(1): Clause(m.group(1), m.group(2).strip())
            for m in re.finditer(r"\*\*(P-\d+\.\d+)\*\*\s+(.+)", self.policy_text)
        }

    def _load(self, name: str) -> dict:
        return json.loads((self.dir / name).read_text())

    # ---- instruments -------------------------------------------------------------------------
    @cached_property
    def alias_index(self) -> list[tuple[str, str]]:
        """(alias_lowercase, symbol), longest alias first so 'hdfc bank' wins over 'hdfc'."""
        pairs = set()
        for sym, r in self.instruments.items():
            pairs.add((sym.lower(), sym))
            for a in r["aliases"]:
                pairs.add((a.lower(), sym))
        return sorted(pairs, key=lambda p: -len(p[0]))

    def resolve_instrument(self, text: str) -> str | None:
        t = text.strip().upper()
        if t in self.instruments:
            return t
        hits = self.find_instruments(text)
        return hits[0][0] if len(hits) == 1 else None

    def find_instruments(self, text: str) -> list[tuple[str, tuple[int, int]]]:
        """All instrument mentions in free text -> [(symbol, span)], non-overlapping, longest-first."""
        low = text.lower()
        taken: list[tuple[int, int]] = []
        out: list[tuple[str, tuple[int, int]]] = []
        for alias, sym in self.alias_index:
            for m in re.finditer(r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])", low):
                s, e = m.span()
                if any(not (e <= a or s >= b) for a, b in taken):
                    continue
                taken.append((s, e))
                out.append((sym, (s, e)))
        return sorted(out, key=lambda x: x[1][0])

    # ---- accounts ----------------------------------------------------------------------------
    def accounts_of(self, user_id: str) -> list[dict]:
        return [a for a in self.accounts.values() if a["owner_id"] == user_id]

    # ---- policy ------------------------------------------------------------------------------
    @cached_property
    def _bm25(self) -> tuple[BM25Okapi, list[str]]:
        ids = list(self.clauses)
        return BM25Okapi([_tok(self.clauses[i].text) for i in ids]), ids

    def search_policy(self, query: str, k: int = 3) -> list[Clause]:
        bm, ids = self._bm25
        scores = bm.get_scores(_tok(query))
        order = sorted(range(len(ids)), key=lambda i: -scores[i])[:k]
        return [self.clauses[ids[i]] for i in order if scores[i] > 0]

    def policy_mentions_number(self, token: str) -> list[str]:
        """Clause ids whose text contains this numeric token (e.g. '0.10%', '₹300')."""
        norm = token.replace(" ", "")
        return [cid for cid, c in self.clauses.items() if norm in c.text.replace(" ", "")]
