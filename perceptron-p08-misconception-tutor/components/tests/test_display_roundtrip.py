"""Display round-trip (review fix, 4 Oct): the expression shown to the LLMs, parsed back, must give the same key and
the same answer for every misconception set as the hidden tokens the labels were computed from."""
from __future__ import annotations

from components.bugs.school_math import decode, parse_display, safe_eval
from components.generator import item_bank
from eval.run_llm_gaps import ALL_SUBSETS, build_inversion, show_llm


def _same(toks, disp) -> bool:
    if safe_eval(disp) != safe_eval(toks):
        return False
    return all(safe_eval(disp, sorted(T)) == safe_eval(toks, sorted(T)) for T in ALL_SUBSETS)


def test_inversion_display_roundtrip():
    bad = [it["item_id"] for it in build_inversion() if not _same(decode(it["tokens"]), parse_display(it["expr"]))]
    assert not bad, bad


def test_tracing_display_roundtrip():
    bad = []
    for g in item_bank(300, seed=2026):
        toks = decode(g.item.params["tokens"])
        if not _same(toks, parse_display(show_llm(toks))):
            bad.append(g.item.item_id)
    assert not bad, bad
