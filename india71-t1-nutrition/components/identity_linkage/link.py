"""Plaintext and privacy-preserving identity linkage for the state identity vault."""

from __future__ import annotations

import hashlib
import hmac
import math
import re
import time
from collections import defaultdict
from datetime import date
from typing import Iterable, Literal

import pandas as pd
from rapidfuzz.distance import JaroWinkler

from architecture.contracts.models import IdentityRecord, LinkDecision, SourceSystem

DEFAULT_VAULT_KEY = b"poshan-setu-demo-vault-key"
DEFAULT_CLK_KEY = b"poshan-setu-demo-clk-key"
HONORIFIC_RE = re.compile(r"\b(md|mohd|mr|mrs|ms|shri|smt|kumari|kumar|baby|of)\.?\b", re.I)
NON_ALPHA_RE = re.compile(r"[^a-z0-9 ]+")
SPACE_RE = re.compile(r"\s+")


def normalise_name(name: str | None) -> str:
    if not name:
        return ""
    s = name.lower().strip()
    s = s.replace("mohammad", "mohammad").replace("muhammad", "mohammad").replace("mohammed", "mohammad")
    replacements = [
        ("ksh", "x"), ("luxmi", "laxmi"), ("lakshmi", "laxmi"), ("w", "v"), ("ee", "i"),
        ("oo", "u"), ("aa", "a"), ("th", "t"), ("ph", "f"), ("q", "k"), ("z", "j"),
    ]
    s = HONORIFIC_RE.sub(" ", s)
    s = NON_ALPHA_RE.sub(" ", s)
    for old, new in replacements:
        s = s.replace(old, new)
    s = re.sub(r"([a-z])\1+", r"\1", s)
    return SPACE_RE.sub(" ", s).strip()


def is_baby_of(name: str | None) -> bool:
    return bool(name and re.search(r"\bbaby\s+of\b", name, re.I))


def phonetic_key(name: str | None) -> str:
    s = normalise_name(name)
    if not s:
        return ""
    tokens = []
    for token in s.split():
        token = re.sub(r"[aeiouh]", "", token[0] + token[1:])
        tokens.append(token[:6])
    return " ".join(tokens)[:12]


def stable_child_key(cluster_id: str, vault_key: bytes = DEFAULT_VAULT_KEY) -> str:
    return hmac.new(vault_key, cluster_id.encode(), hashlib.sha256).hexdigest()


def records_from_frame(df: pd.DataFrame) -> list[IdentityRecord]:
    rows = []
    for row in df.to_dict(orient="records"):
        rows.append({k: (v if isinstance(v, dict) or not pd.isna(v) else None) for k, v in row.items()})
    return [IdentityRecord.model_validate(row) for row in rows]


def _birth_year(d: date | None) -> int | None:
    return d.year if d else None


def _shared_id_pairs(a: IdentityRecord, b: IdentityRecord) -> set[tuple[str, str]]:
    return set(a.shared_ids.items()) & set(b.shared_ids.items())


def _decision(members: list[IdentityRecord], method: Literal["deterministic", "probabilistic", "clerical_review", "singleton"], probability: float, cluster_id: str, vault_key: bytes) -> LinkDecision:
    return LinkDecision(
        child_key=stable_child_key(cluster_id, vault_key),
        members=[(m.source, m.source_record_id) for m in members],
        method=method,
        match_probability=max(0.0, min(1.0, probability)),
        synthetic=all(m.synthetic for m in members),
    )


def _name_sim(a: str | None, b: str | None) -> float:
    na, nb = normalise_name(a), normalise_name(b)
    if not na or not nb:
        return 0.35
    return JaroWinkler.normalized_similarity(na, nb)


def _dob_score(a: date | None, b: date | None) -> float:
    if not a or not b:
        return 0.45
    delta = abs((a - b).days)
    if delta == 0:
        return 1.0
    if a.year == b.year and a.month == b.month and (a.day == 1 or b.day == 1):
        return 0.82
    if a.month == 1 and a.day == 1 and a.year == b.year or b.month == 1 and b.day == 1 and a.year == b.year:
        return 0.68
    if delta <= 3:
        return 0.82
    if delta <= 14:
        return 0.65
    if a.year == b.year:
        return 0.45
    return 0.05


def pair_score(a: IdentityRecord, b: IdentityRecord) -> float:
    child_sim = _name_sim(a.child_name, b.child_name)
    if is_baby_of(a.child_name) or is_baby_of(b.child_name):
        child_sim = 0.58 + 0.38 * _name_sim(a.mother_name, b.mother_name)
    mother_sim = _name_sim(a.mother_name, b.mother_name)
    father_sim = _name_sim(a.father_name, b.father_name)
    dob = _dob_score(a.dob, b.dob)
    sex = 0.08 if a.sex and b.sex and a.sex != b.sex else 1.0
    village = 1.0 if a.village_code and a.village_code == b.village_code else 0.35
    raw = 2.3 * child_sim + 2.0 * mother_sim + 1.45 * dob + 0.45 * father_sim + 0.45 * village + 0.35 * sex - 4.15
    return 1.0 / (1.0 + math.exp(-raw))


def _blocks(records: Iterable[IdentityRecord]) -> dict[tuple[str, object], list[IdentityRecord]]:
    out: dict[tuple[str, object], list[IdentityRecord]] = defaultdict(list)
    for r in records:
        if r.village_code and r.dob:
            out[("vy", r.village_code, r.dob.year)].append(r)
            out[("vy", r.village_code, r.dob.year - 1)].append(r)
            out[("vy", r.village_code, r.dob.year + 1)].append(r)
        mp = phonetic_key(r.mother_name)
        if mp:
            out[("m", mp[:8])].append(r)
    return out


def deterministic_links(poshan: list[IdentityRecord], health: list[IdentityRecord], vault_key: bytes = DEFAULT_VAULT_KEY) -> tuple[list[LinkDecision], set[str], set[str]]:
    decisions: list[LinkDecision] = []
    used_p: set[str] = set()
    used_h: set[str] = set()
    h_by_id: dict[tuple[str, str], list[IdentityRecord]] = defaultdict(list)
    for h in health:
        for item in h.shared_ids.items():
            h_by_id[item].append(h)
    for p in poshan:
        if p.source_record_id in used_p:
            continue
        candidates = []
        for item in p.shared_ids.items():
            candidates.extend(h_by_id.get(item, []))
        candidates = [h for h in candidates if h.source_record_id not in used_h and _shared_id_pairs(p, h)]
        if candidates:
            h = candidates[0]
            used_p.add(p.source_record_id)
            used_h.add(h.source_record_id)
            cluster = "id:" + sorted(_shared_id_pairs(p, h))[0][1]
            decisions.append(_decision([p, h], "deterministic", 1.0, cluster, vault_key))
    return decisions, used_p, used_h


def _candidate_scores(poshan: list[IdentityRecord], health: list[IdentityRecord], used_p: set[str], used_h: set[str], scorer) -> list[tuple[float, IdentityRecord, IdentityRecord]]:
    h_blocks = _blocks(h for h in health if h.source_record_id not in used_h)
    scored: list[tuple[float, IdentityRecord, IdentityRecord]] = []
    seen: set[tuple[str, str]] = set()
    for p in poshan:
        if p.source_record_id in used_p:
            continue
        keys = []
        if p.village_code and p.dob:
            keys += [("vy", p.village_code, p.dob.year - 1), ("vy", p.village_code, p.dob.year), ("vy", p.village_code, p.dob.year + 1)]
        mp = phonetic_key(p.mother_name)
        if mp:
            keys.append(("m", mp[:8]))
        for key in keys:
            for h in h_blocks.get(key, []):
                pair = (p.source_record_id, h.source_record_id)
                if pair in seen:
                    continue
                seen.add(pair)
                s = scorer(p, h)
                if s >= 0.45:
                    scored.append((s, p, h))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored


def link_plaintext(poshan: list[IdentityRecord], health: list[IdentityRecord], threshold: float = 0.82, clerical_low: float = 0.68, vault_key: bytes = DEFAULT_VAULT_KEY) -> list[LinkDecision]:
    decisions, used_p, used_h = deterministic_links(poshan, health, vault_key)
    for score, p, h in _candidate_scores(poshan, health, used_p, used_h, pair_score):
        if p.source_record_id in used_p or h.source_record_id in used_h:
            continue
        if score >= threshold:
            used_p.add(p.source_record_id); used_h.add(h.source_record_id)
            decisions.append(_decision([p, h], "probabilistic", score, f"prob:{p.source.value}:{p.source_record_id}|{h.source.value}:{h.source_record_id}", vault_key))
        elif score >= clerical_low:
            used_p.add(p.source_record_id); used_h.add(h.source_record_id)
            decisions.append(_decision([p, h], "clerical_review", score, f"clerical:{p.source_record_id}|{h.source_record_id}", vault_key))
    return decisions


def _bigrams(value: str) -> list[str]:
    v = f"^{value}$"
    return [v[i:i+2] for i in range(max(0, len(v) - 1))]


def clk_bits(record: IdentityRecord, key: bytes = DEFAULT_CLK_KEY, size: int = 1000, k: int = 20) -> int:
    fields = [
        "child:" + (normalise_name(record.child_name) if not is_baby_of(record.child_name) else "baby_of_" + normalise_name(record.mother_name)),
        "mother:" + normalise_name(record.mother_name),
        "father:" + normalise_name(record.father_name),
        "dob:" + (record.dob.isoformat() if record.dob else ""),
        "sex:" + (record.sex.value if record.sex else ""),
        "village:" + (record.village_code or ""),
    ]
    bits = 0
    for field in fields:
        weight = 2 if field.startswith(("child", "mother")) else 1
        for gram in _bigrams(field):
            digest = hmac.new(key, gram.encode(), hashlib.sha256).digest()
            for i in range(k * weight):
                start = (i * 2) % (len(digest) - 1)
                pos = int.from_bytes(digest[start:start+2], "big") % size
                bits |= 1 << pos
    return bits


def dice_bits(a: int, b: int) -> float:
    ca, cb = a.bit_count(), b.bit_count()
    if not ca or not cb:
        return 0.0
    return 2.0 * (a & b).bit_count() / (ca + cb)


def link_pprl_bloom(poshan: list[IdentityRecord], health: list[IdentityRecord], threshold: float = 0.91, clerical_low: float = 0.86, vault_key: bytes = DEFAULT_VAULT_KEY, clk_key: bytes = DEFAULT_CLK_KEY) -> list[LinkDecision]:
    decisions, used_p, used_h = deterministic_links(poshan, health, vault_key)
    p_bits = {p.source_record_id: clk_bits(p, clk_key) for p in poshan}
    h_bits = {h.source_record_id: clk_bits(h, clk_key) for h in health}
    def scorer(p: IdentityRecord, h: IdentityRecord) -> float:
        base = dice_bits(p_bits[p.source_record_id], h_bits[h.source_record_id])
        if p.sex and h.sex and p.sex != h.sex:
            base -= 0.06
        return max(0.0, min(1.0, base))
    for score, p, h in _candidate_scores(poshan, health, used_p, used_h, scorer):
        if p.source_record_id in used_p or h.source_record_id in used_h:
            continue
        if score >= threshold:
            used_p.add(p.source_record_id); used_h.add(h.source_record_id)
            decisions.append(_decision([p, h], "probabilistic", score, f"pprl:{p.source.value}:{p.source_record_id}|{h.source.value}:{h.source_record_id}", vault_key))
        elif score >= clerical_low:
            used_p.add(p.source_record_id); used_h.add(h.source_record_id)
            decisions.append(_decision([p, h], "clerical_review", score, f"pprl-clerical:{p.source_record_id}|{h.source_record_id}", vault_key))
    return decisions


def link_from_frames(poshan_df: pd.DataFrame, health_df: pd.DataFrame, method: Literal["ids", "plaintext", "pprl"] = "plaintext") -> list[LinkDecision]:
    poshan = records_from_frame(poshan_df)
    health = records_from_frame(health_df)
    if method == "ids":
        return deterministic_links(poshan, health)[0]
    if method == "pprl":
        return link_pprl_bloom(poshan, health)
    return link_plaintext(poshan, health)


def timed_link(poshan_df: pd.DataFrame, health_df: pd.DataFrame, method: Literal["ids", "plaintext", "pprl"]):
    start = time.perf_counter()
    decisions = link_from_frames(poshan_df, health_df, method)
    return decisions, time.perf_counter() - start
