"""Argument provenance: for each argument of a proposed call, find where its value came from.

A value is grounded only if a trusted source states it: the user's words, the reference KB, or
structured tool data. A value found only in untrusted text (emails, tickets) is treated as possible
injection; a value found nowhere is unverifiable (absence of evidence, not contradiction).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from architecture.contracts.models import Context, Evidence, Trust
from components.kb.kb import ReferenceKB

BUY_WORDS = r"\b(buy|buying|purchase|add|accumulate|acquire|go long|pick up)\b"
SELL_WORDS = r"\b(sell|selling|exit|trim|offload|dispose|liquidate|reduce|book profits?)\b"
TOOL_INTENT = {
    "place_order": r"\b(buy|sell|purchase|order|add|exit|trim|accumulate|acquire|offload|liquidate|reduce)\b",
    "cancel_order": r"\b(cancel|withdraw|pull|kill|revoke)\b",
    "transfer_funds": r"\b(transfer|move|shift|wire|send)\b.*\b(funds?|money|cash|₹|rs\.?|inr|lakh|crore|\d)",
    "send_client_message": r"\b(tell|inform|message|notify|email|let .* know|reply|write to|confirm to)\b",
}
_NUM = re.compile(
    r"(?P<cur>₹|rs\.?\s?|inr\s?)?(?P<num>\d[\d,]*(?:\.\d+)?)\s?(?P<mult>k\b|lakh\b|lakhs\b|lac\b|l\b|crore\b|cr\b)?",
    re.I,
)
_MULT = {"k": 1e3, "lakh": 1e5, "lakhs": 1e5, "lac": 1e5, "l": 1e5, "crore": 1e7, "cr": 1e7}
ACCOUNT_RE = re.compile(r"\bA-\d{4}\b")
ORDER_RE = re.compile(r"\bORD-\d+\b")


@dataclass
class NumberMention:
    value: float
    kind: str  # qty | price | amount | unknown
    span: tuple[int, int]
    text: str


@dataclass
class Mentions:
    """Everything the user's own words commit to."""

    text: str
    numbers: list[NumberMention] = field(default_factory=list)
    instruments: list[tuple[str, tuple[int, int]]] = field(default_factory=list)
    accounts: list[tuple[str, tuple[int, int]]] = field(default_factory=list)
    orders: list[tuple[str, tuple[int, int]]] = field(default_factory=list)
    side: str | None = None  # buy | sell | None (absent or ambiguous)
    market: bool = False
    tool_intents: set[str] = field(default_factory=set)


def parse_numbers(text: str, protected: list[tuple[int, int]]) -> list[NumberMention]:
    out = []
    low = text.lower()
    for m in _NUM.finditer(low):
        s, e = m.span()
        if any(a <= s < b for a, b in protected):  # inside an ID like A-1001 or ORD-7
            continue
        if s > 0 and (low[s - 1].isalpha() or low[s - 1] == "-"):
            continue
        raw = m.group("num").replace(",", "")
        try:
            v = float(raw)
        except ValueError:
            continue
        mult = (m.group("mult") or "").lower()
        if mult:
            v *= _MULT[mult]
        before, after = low[max(0, s - 14):s], low[e:e + 14]
        if re.match(r"\s*(shares?|qty|units?|stocks?|nos\.?)\b", after):
            kind = "qty"
        elif re.search(r"(\bat|@|\blimit(?: price)?(?: of)?|\bprice(?: of)?)\s*(₹|rs\.?|inr)?\s*$", before):
            kind = "price"
        elif m.group("cur") or mult in ("lakh", "lakhs", "lac", "l", "crore", "cr"):
            kind = "amount"
        elif re.search(r"\b(buy|sell|purchase|add|exit|trim|acquire|offload)\s*$", before):
            kind = "qty"
        else:
            kind = "unknown"
        out.append(NumberMention(v, kind, (s, e), text[s:e].strip()))
    return out


def extract_mentions(text: str, kb: ReferenceKB) -> Mentions:
    low = text.lower()
    accounts = [(m.group(0), m.span()) for m in ACCOUNT_RE.finditer(text)]
    orders = [(m.group(0), m.span()) for m in ORDER_RE.finditer(text)]
    protected = [s for _, s in accounts + orders]
    buy, sell = bool(re.search(BUY_WORDS, low)), bool(re.search(SELL_WORDS, low))
    return Mentions(
        text=text,
        numbers=parse_numbers(text, protected),
        instruments=kb.find_instruments(text),
        accounts=accounts,
        orders=orders,
        side="buy" if buy and not sell else "sell" if sell and not buy else None,
        market=bool(re.search(r"\b(at market|market order|at the market|mkt)\b", low)),
        tool_intents={t for t, rx in TOOL_INTENT.items() if re.search(rx, low)},
    )


def _walk(obj: Any, path: str):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk(v, f"{path}[{i}]")
    else:
        yield path, obj


def find_in_observations(ctx: Context, value: Any, rel_tol: float = 0.0) -> list[Evidence]:
    """Every observation leaf that states this value (numbers within rel_tol; strings case-insensitive,
    also as a substring of free text so injected instructions are found)."""
    hits = []
    for i, ob in enumerate(ctx.observations):
        for path, leaf in _walk(ob.result, f"obs[{i}].result"):
            ok = False
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                if isinstance(leaf, (int, float)) and not isinstance(leaf, bool):
                    ok = abs(leaf - value) <= rel_tol * max(abs(value), 1e-9)
                elif isinstance(leaf, str):
                    ok = any(abs(n.value - value) <= rel_tol * max(abs(value), 1e-9)
                             for n in parse_numbers(leaf, []))
            elif isinstance(value, str) and isinstance(leaf, str):
                ok = value.lower() == leaf.lower() or (len(value) >= 4 and value.lower() in leaf.lower())
            if ok:
                hits.append(Evidence(source=ob.trust, locator=path, snippet=str(leaf)[:120]))
    return hits


def trusted(evs: list[Evidence]) -> list[Evidence]:
    return [e for e in evs if e.source != Trust.UNTRUSTED]
