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


def counts(path: Path) -> dict:
    """Row-level counts, so quoted percentages are computed once from integers (no double rounding)."""
    d = j(path)
    rows = d["rows"]
    good = [r for r in rows if r["kind"] == "good"] if "kind" in rows[0] else [r for r in rows if r["should_execute"]]
    bad = [r for r in rows if r["kind"] == "bad_harmful"] if "kind" in rows[0] else [r for r in rows if not r["should_execute"]]
    return {"n": len(rows), "good": len(good), "bad": len(bad),
            "stop": sum(r["decision"] != "allow" for r in bad), "hard": sum(r["decision"] == "block" for r in bad),
            "fb": sum(r["decision"] == "block" for r in good), "hold": sum(r["decision"] == "escalate" for r in good),
            "good_stop": sum(r["decision"] != "allow" for r in good), "m": d["metrics"]}


def pc(k: int, n: int, nd: int = 0) -> str:
    v = 100 * k / n
    return f"{v:.{nd}f}%" if nd else f"{int(v + 0.5)}%"


def ci(c: list[float]) -> str:
    return f"{int(100 * c[0] + 0.5)}–{int(100 * c[1] + 0.5)}"


def claims() -> list[tuple[Path, str]]:
    v0, bal = counts(T / "t0_v0__test.json"), counts(T / "t0_balanced__test.json")
    dev, sch = counts(T / "t0_balanced__dev.json"), counts(T / "schema__test.json")
    bs, jd = counts(T / "t0_balanced__test__sample300.json"), counts(T / "llm_judge__test__sample300.json")
    astra = counts(R / "first_run" / "t0__test__astra_redteam.json")
    synth = counts(R / "t0__test.json")
    audit = (ROOT / "eval" / "taubench" / "audit-test-misses.md").read_text()
    n_user = len(re.findall(r"\| A user-requested \|", audit))
    n_entity = len(re.findall(r"\| B wrong entity \|", audit))
    assert sch["stop"] == 0 and jd["hold"] == 0
    assert bal["m"]["score"] < v0["m"]["score"], "abstract says the tuned setting does not beat v0"
    out = [
        (ABSTRACT, f"{dev['n'] + bal['n']:,} calls"),
        (ABSTRACT, f"({bal['n']} calls, {bal['bad']} harmful)"),
        (ABSTRACT, "Schema checks catch 0%"),
        (ABSTRACT, f"**{pc(v0['stop'], v0['bad'])} (95% CI {ci(v0['m']['ci95_cluster_bootstrap']['catch_harmful'])})** of harmful calls"),
        (ABSTRACT, f"blocks {pc(v0['fb'], v0['good'])} of good calls and holds {pc(v0['hold'], v0['good'])}"),
        (ABSTRACT, f"cuts false blocks to **{pc(bal['fb'], bal['good'], 1)}** and holds to {pc(bal['hold'], bal['good'])}"),
        (ABSTRACT, f"stopping **{pc(bal['stop'], bal['bad'])} ({ci(bal['m']['ci95_cluster_bootstrap']['catch_harmful'])})**"),
        (ABSTRACT, f"**{bal['m']['latency_ms_p95']:.1f} ms** at p95"),
        (ABSTRACT, f"Only {bal['hard']} of its stops are hard blocks"),
        (ABSTRACT, f"at almost the same good-call stop rate ({pc(jd['good_stop'], jd['good'])} vs our {pc(bs['good_stop'], bs['good'])})"),
        (ABSTRACT, f"the judge stops {pc(jd['stop'], jd['bad'])} of harmful calls and ours {pc(bs['stop'], bs['bad'])}"),
        (ABSTRACT, f"{n_user} were explicitly requested"),
        (ABSTRACT, f"{n_entity} were wrong-entity choices"),
        (ABSTRACT, f"{astra['n']} cases written by a different model family"),
        (ABSTRACT, f"stops {pc(astra['stop'], astra['bad'])} ({ci(astra['m']['ci95_wilson']['catch_rate'])}) of {astra['bad']} bad calls"),
        (ABSTRACT, f"blocks {pc(astra['fb'], astra['good'])} and holds {pc(astra['hold'], astra['good'])} of {astra['good']} good ones"),
        (ABSTRACT, f"synthetic suite scores {pc(synth['stop'], synth['bad'])} caught, {pc(synth['fb'], synth['good'])} false blocks"),
    ]
    b = {r["item_id"]: r for r in j(T / "t0_balanced__test__sample300.json")["rows"]}
    c = {r["item_id"]: r for r in j(T / "cascade_fast__test__sample300.json")["rows"]}
    held = [i for i, r in b.items() if r["decision"] == "escalate" and r["kind"] in ("good", "bad_harmful")]
    settled = [i for i in held if c[i]["decision"] != "escalate"]
    ok_block = sum(c[i]["decision"] == "block" and b[i]["kind"] == "bad_harmful" for i in settled)
    bad_block = sum(c[i]["decision"] == "block" and b[i]["kind"] == "good" for i in settled)
    released = sum(c[i]["decision"] == "allow" for i in settled)
    out.append((ABSTRACT, f"settled {len(settled)} of {len(held)} held calls ({ok_block} harmful correctly blocked, "
                          f"{bad_block} good calls wrongly blocked) and released {'none' if released == 0 else released}"))
    return out


def main() -> int:
    bad = 0
    texts: dict[Path, str] = {}
    for doc, s in claims():
        texts.setdefault(doc, doc.read_text())
        if s not in texts[doc]:
            bad += 1
            print(f"MISSING in {doc.relative_to(ROOT)}: {s!r}")
    texts.setdefault(ABSTRACT, ABSTRACT.read_text())
    if "[CASCADE-SENTENCE]" in texts[ABSTRACT] or "[ASTRA" in texts[ABSTRACT] or "[JUDGE" in texts[ABSTRACT]:
        bad += 1
        print("abstract still contains a result placeholder")
    words = len(re.sub(r"[*#`]", "", texts[ABSTRACT].split("## Problem", 1)[1]).split())
    if not 600 <= words <= 900:
        bad += 1
        print(f"abstract body is {words} words (must be 600-900)")
    print(f"check_docs: {len(claims())} claims, {bad} problems, abstract {words} words")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
