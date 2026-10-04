"""Privacy-preserving record linkage with an explicit department boundary (encode on each side, match encodings only).

Each department runs `encode_department` on its own records, with a secret key that the two departments share and the
matcher never receives. Only these columns cross the boundary (`ALLOWED_COLUMNS`):

  source, record_id  which system and which of its records; the matcher uses them as opaque labels, never as evidence
  clk                1,000-bit Bloom filter (CLK) of keyed bigrams of child/mother/father name, DOB, sex and village (hex)
  block_tokens       keyed-HMAC tokens of link.py's blocking keys: village x birth-year band, mother-name phonetic code
  id_tokens          keyed-HMAC tokens of shared programme IDs (RCH ID, U-WIN ID, Poshan Tracker beneficiary ID)
  sex_token          keyed-HMAC token of recorded sex, so the matcher sees agreement, not the value
  synthetic          provenance flag

`match_encoded` refuses any other column and reproduces `link.link_pprl_bloom` decision for decision: the same
shared-ID step, blocking, Dice score with the sex-disagreement penalty, greedy one-to-one assignment and thresholds.
(Only the child_key of an ID-joined pair differs: it is derived from the ID token instead of the plaintext ID.)

What the matcher can still learn: which records share a blocking, ID or sex token, and the Bloom filters themselves.
Bloom-filter encodings are open to published frequency and pattern-mining attacks; keyed hashing is not anonymisation,
and hardening (salting, balancing, rotating keys) is a pilot item.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from collections import defaultdict
from typing import Iterable

import pandas as pd

from architecture.contracts.models import IdentityRecord, LinkDecision, SourceSystem
from components.identity_linkage.link import (DEFAULT_VAULT_KEY, clk_bits, dice_bits, phonetic_key, records_from_frame,
                                              stable_child_key)

ALLOWED_COLUMNS = ("source", "record_id", "clk", "block_tokens", "id_tokens", "sex_token", "synthetic")
CLK_SIZE = 1000
SEX_PENALTY = 0.06  # link.link_pprl_bloom's penalty when both sexes are recorded and differ
CANDIDATE_FLOOR = 0.45  # link._candidate_scores keeps pairs scoring at least this


def _subkey(secret_key: bytes, purpose: str) -> bytes:
    return hmac.new(secret_key, b"poshan-setu-pprl/" + purpose.encode(), hashlib.sha256).digest()


def _token(key: bytes, value: object) -> str:
    return hmac.new(key, json.dumps(value, separators=(",", ":")).encode(), hashlib.sha256).hexdigest()


def blocking_keys(record: IdentityRecord) -> list[list]:
    """The blocking keys of link._blocks / link._candidate_scores, in the order the query side looks them up."""
    keys: list[list] = []
    if record.village_code and record.dob:
        year = record.dob.year
        keys += [["vy", record.village_code, year - 1], ["vy", record.village_code, year], ["vy", record.village_code, year + 1]]
    mp = phonetic_key(record.mother_name)
    if mp:
        keys.append(["m", mp[:8]])
    return keys


def encode_record(record: IdentityRecord, secret_key: bytes) -> dict:
    k_block, k_id, k_sex = _subkey(secret_key, "block"), _subkey(secret_key, "id"), _subkey(secret_key, "sex")
    return {
        "source": record.source.value,
        "record_id": record.source_record_id,
        "clk": format(clk_bits(record, secret_key, size=CLK_SIZE), f"0{CLK_SIZE // 4}x"),
        "block_tokens": [_token(k_block, key) for key in blocking_keys(record)],
        "id_tokens": [_token(k_id, [name, value]) for name, value in record.shared_ids.items()],
        "sex_token": _token(k_sex, record.sex.value) if record.sex else None,
        "synthetic": bool(record.synthetic),
    }


def encode_department(records_df: pd.DataFrame, secret_key: bytes) -> pd.DataFrame:
    """Runs inside one department. `records_df` has IdentityRecord columns (names, DOB, village, sex, shared IDs).
    The CLK is keyed with `secret_key` itself (as in link.clk_bits); the tokens with sub-keys derived from it."""
    rows = [encode_record(r, secret_key) for r in records_from_frame(records_df)]
    return pd.DataFrame(rows, columns=list(ALLOWED_COLUMNS))


def check_boundary(enc: pd.DataFrame, name: str = "encoded frame") -> None:
    """Fail closed: the matcher accepts exactly ALLOWED_COLUMNS."""
    cols = set(enc.columns)
    if cols != set(ALLOWED_COLUMNS):
        extra, missing = sorted(cols - set(ALLOWED_COLUMNS)), sorted(set(ALLOWED_COLUMNS) - cols)
        raise ValueError(f"{name}: not an encoded frame (not allowed across the boundary: {extra}; missing: {missing})")


def _text(value) -> str | None:
    return value if isinstance(value, str) and value else None


def _decision(a: dict, b: dict, method: str, probability: float, cluster_id: str, vault_key: bytes) -> LinkDecision:
    return LinkDecision(
        child_key=stable_child_key(cluster_id, vault_key),
        members=[(SourceSystem(a["source"]), a["record_id"]), (SourceSystem(b["source"]), b["record_id"])],
        method=method,
        match_probability=max(0.0, min(1.0, probability)),
        synthetic=bool(a["synthetic"]) and bool(b["synthetic"]),
    )


def match_encoded(enc_a: pd.DataFrame, enc_b: pd.DataFrame, threshold: float = 0.91, clerical_low: float = 0.86,
                  vault_key: bytes = DEFAULT_VAULT_KEY) -> list[LinkDecision]:
    """Runs at the matcher, which holds only the two encoded frames (A = Poshan Tracker side, B = health side)."""
    check_boundary(enc_a, "enc_a")
    check_boundary(enc_b, "enc_b")
    A = enc_a.to_dict(orient="records")
    B = enc_b.to_dict(orient="records")
    decisions: list[LinkDecision] = []
    used_a: set[str] = set()
    used_b: set[str] = set()

    # 1. shared programme IDs, compared as keyed tokens (link.deterministic_links)
    b_by_id: dict[str, list[dict]] = defaultdict(list)
    for b in B:
        for tok in b["id_tokens"]:
            b_by_id[tok].append(b)
    for a in A:
        if a["record_id"] in used_a:
            continue
        a_ids = set(a["id_tokens"])
        candidates: list[dict] = []
        for tok in a["id_tokens"]:
            candidates.extend(b_by_id.get(tok, []))
        candidates = [b for b in candidates if b["record_id"] not in used_b and a_ids & set(b["id_tokens"])]
        if candidates:
            b = candidates[0]
            used_a.add(a["record_id"])
            used_b.add(b["record_id"])
            decisions.append(_decision(a, b, "deterministic", 1.0, "id:" + sorted(a_ids & set(b["id_tokens"]))[0], vault_key))

    # 2. Dice on the Bloom filters within keyed blocks (link._candidate_scores + link.link_pprl_bloom's scorer)
    bits_a = {a["record_id"]: int(a["clk"], 16) for a in A}
    bits_b = {b["record_id"]: int(b["clk"], 16) for b in B}

    def score(a: dict, b: dict) -> float:
        s = dice_bits(bits_a[a["record_id"]], bits_b[b["record_id"]])
        sa, sb = _text(a["sex_token"]), _text(b["sex_token"])
        if sa and sb and sa != sb:
            s -= SEX_PENALTY
        return max(0.0, min(1.0, s))

    b_blocks: dict[str, list[dict]] = defaultdict(list)
    for b in B:
        if b["record_id"] in used_b:
            continue
        for tok in b["block_tokens"]:
            b_blocks[tok].append(b)
    scored: list[tuple[float, dict, dict]] = []
    seen: set[tuple[str, str]] = set()
    for a in A:
        if a["record_id"] in used_a:
            continue
        for tok in a["block_tokens"]:
            for b in b_blocks.get(tok, []):
                pair = (a["record_id"], b["record_id"])
                if pair in seen:
                    continue
                seen.add(pair)
                s = score(a, b)
                if s >= CANDIDATE_FLOOR:
                    scored.append((s, a, b))
    scored.sort(key=lambda x: x[0], reverse=True)

    # 3. greedy one-to-one assignment (link.link_pprl_bloom)
    for s, a, b in scored:
        if a["record_id"] in used_a or b["record_id"] in used_b:
            continue
        if s >= threshold:
            used_a.add(a["record_id"])
            used_b.add(b["record_id"])
            decisions.append(_decision(a, b, "probabilistic", s, f"pprl:{a['source']}:{a['record_id']}|{b['source']}:{b['record_id']}", vault_key))
        elif s >= clerical_low:
            used_a.add(a["record_id"])
            used_b.add(b["record_id"])
            decisions.append(_decision(a, b, "clerical_review", s, f"pprl-clerical:{a['record_id']}|{b['record_id']}", vault_key))
    return decisions


def accept_at(decisions: Iterable[LinkDecision], threshold: float, vault_key: bytes = DEFAULT_VAULT_KEY) -> list[LinkDecision]:
    """Decisions exactly as `match_encoded` returns them with another acceptance threshold (>= the clerical_low used).
    Every pair scoring >= clerical_low reserves its two records whichever label it gets, so the one-to-one assignment
    does not depend on the threshold; only the probabilistic/clerical label (and its child_key) does."""
    out = []
    for d in decisions:
        if d.method in ("probabilistic", "clerical_review"):
            method = "probabilistic" if d.match_probability >= threshold else "clerical_review"
            if method != d.method:
                (sa, ia), (sb, ib) = d.members
                cluster = f"pprl:{sa.value}:{ia}|{sb.value}:{ib}" if method == "probabilistic" else f"pprl-clerical:{ia}|{ib}"
                d = d.model_copy(update={"method": method, "child_key": stable_child_key(cluster, vault_key)})
        out.append(d)
    return out
