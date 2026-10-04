"""Fail if a number quoted in the deliverables differs from the committed eval results (anti-drift check).

Each claim pairs a document with a string that must appear in it verbatim, computed from eval/results/.
Run: .venv/bin/python -m eval.check_docs        (exit code 1 on any mismatch; also run by pytest)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "eval" / "results"
T = R / "taubench"
ABSTRACT = ROOT / "deliverables" / "round1-abstract.md"


def j(p: Path) -> dict:
    return json.loads(p.read_text())


def p0(x: float) -> str:
    return f"{round(100 * x)}%"


def p1(x: float) -> str:
    return f"{100 * x:.1f}%"


def ci0(ci: list[float]) -> str:
    return f"{round(100 * ci[0])}–{round(100 * ci[1])}"


def claims() -> list[tuple[Path, str]]:
    v0, bal = j(T / "t0_v0__test.json")["metrics"], j(T / "t0_balanced__test.json")["metrics"]
    sch = j(T / "schema__test.json")["metrics"]
    dev = j(T / "t0_balanced__dev.json")["metrics"]
    judge = j(T / "llm_judge__test__sample300.json")["metrics"]
    casc = j(T / "cascade_fast__test__sample300.json")["metrics"]
    bal_s = j(T / "t0_balanced__test__sample300.json")["metrics"]
    fr = j(T / "frontier__test__sample300.json")
    astra = j(R / "t0__test__astra_redteam.json")["metrics"]
    astra_schema = j(R / "schema__test__astra_redteam.json")["metrics"]
    synth = j(R / "t0__test.json")["metrics"]
    audit = (ROOT / "eval" / "taubench" / "audit-test-misses.md").read_text()
    n_user = len(re.findall(r"\| A user-requested \|", audit))
    n_entity = len(re.findall(r"\| B wrong entity \|", audit))
    assert sch["catch_harmful"] == 0.0
    assert astra_schema["catch_rate"] == 0.0
    out = [
        (ABSTRACT, f"{dev['n'] + bal['n']:,} calls"),
        (ABSTRACT, f"({bal['n']} calls, {bal['n_harmful']} harmful)"),
        (ABSTRACT, "Schema checks catch 0%"),
        (ABSTRACT, f"catches **{p0(v0['catch_harmful'])} (95% CI {ci0(v0['ci95_cluster_bootstrap']['catch_harmful'])})**"),
        (ABSTRACT, f"blocks {p0(v0['false_block_rate'])} of good calls and escalates {p0(v0['escalation_rate'])}"),
        (ABSTRACT, f"cuts false blocks to **{p1(bal['false_block_rate'])}** and escalations to {p0(bal['escalation_rate'])}"),
        (ABSTRACT, f"catching **{p0(bal['catch_harmful'])} ({ci0(bal['ci95_cluster_bootstrap']['catch_harmful'])})**"),
        (ABSTRACT, f"**{bal['latency_ms_p95']:.1f} ms** at p95"),
        (ABSTRACT, f"the LLM judge catches {p0(judge['catch_harmful'])} of harmful calls but blocks {p0(judge['false_block_rate'])} of good ones"),
        (ABSTRACT, f"median {judge['latency_ms_p50'] / 1000:.1f} s per call"),
        (ABSTRACT, f"escalations on good calls from {p0(bal_s['escalation_rate'])} to {p0(casc['escalation_rate'])}"),
        (ABSTRACT, f"harmful-call catch from {p0(bal_s['catch_harmful'])} to {p0(casc['catch_harmful'])}"),
        (ABSTRACT, f"{n_user} that the simulated user explicitly requested"),
        (ABSTRACT, f"{n_entity} wrong-entity choices"),
        (ABSTRACT, f"{astra['n']} cases written by a different model family"),
        (ABSTRACT, f"catches {p0(astra['catch_rate'])} ({ci0(astra['ci95_wilson']['catch_rate'])}) of {astra['n_bad']} bad calls"),
        (ABSTRACT, f"blocks {p0(astra['false_block_rate'])} and escalates {p0(astra['escalation_rate'])} of {astra['n_good']} good ones"),
        (ABSTRACT, f"our own synthetic suite ({p0(synth['catch_rate'])} caught, {p0(synth['false_block_rate'])} false blocks)"),
    ]
    m = fr["llm_judge_matched"]["t0_balanced"]
    out.append((ABSTRACT, f"at the same good-call stop rate ({p0(m['our_good_stop'])}) the judge catches {p0(m['judge_catch_at_same_stop'])}"))
    return out


def main() -> int:
    bad = 0
    texts: dict[Path, str] = {}
    for doc, s in claims():
        texts.setdefault(doc, doc.read_text())
        if s not in texts[doc]:
            bad += 1
            print(f"MISSING in {doc.relative_to(ROOT)}: {s!r}")
    words = len(re.sub(r"[*#`]", "", texts[ABSTRACT].split("## Problem", 1)[1]).split())
    if not 600 <= words <= 900:
        bad += 1
        print(f"abstract body is {words} words (must be 600-900)")
    print(f"check_docs: {len(claims())} claims, {bad} problems, abstract {words} words")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
