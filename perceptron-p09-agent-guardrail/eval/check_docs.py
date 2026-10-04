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


def pc_f(x: float) -> str:
    return f"{int(100 * x + 0.5)}%"


def ci(c: list[float]) -> str:
    return f"{int(100 * c[0] + 0.5)}–{int(100 * c[1] + 0.5)}"


def claims() -> list[tuple[Path, str]]:
    v0, bal = counts(T / "t0_v0__test.json"), counts(T / "t0_balanced__test.json")
    dev, sch = counts(T / "t0_balanced__dev.json"), counts(T / "schema__test.json")
    full = j(T / "t0_balanced__test.json")["metrics"]
    bs, st = counts(T / "t0_balanced__test__sample300.json"), counts(T / "t0_strict__test__sample300.json")
    jd, j4, ca = (counts(T / f"{g}__test__sample300.json") for g in ("llm_judge", "llm_judge_aoai", "cascade_aoai"))
    cost, fr = j(T / "cost__test__sample300.json"), j(T / "frontier__test__sample300.json")
    astra, synth = counts(R / "t0__test__astra_redteam.json"), counts(R / "t0__test.json")
    readme = ROOT / "eval" / "taubench" / "README.md"
    lat = j(T / "latency__test.json")
    audit = (ROOT / "eval" / "taubench" / "audit-test-misses.md").read_text()
    n_user = len(re.findall(r"\| A user-requested \|", audit))
    entity_ids = [m.strip() for m in re.findall(r"\| \d+ \| ([^|]+) \| B wrong entity \|", audit)]
    cur = {r["item_id"]: r["decision"] for r in j(T / "t0_balanced__test.json")["rows"]}
    assert sch["stop"] == 0 and bal["m"]["score"] < v0["m"]["score"]
    assert all(cur[i] == "allow" for i in entity_ids), "abstract says all wrong-entity misses still pass Tier 0"
    # LLM-judge rows at the test-selected risk threshold, and the hosted cascade's transitions from balanced holds
    from eval.taubench.frontier import risk_of
    jr = {r["item_id"]: r for r in j(T / "llm_judge_aoai__test__sample300.json")["rows"]}
    thr = fr["llm_judge_aoai_matched"]["t0_strict"]["judge_threshold"]
    j_thr = sum((risk_of(r) if risk_of(r) is not None else 100) >= thr for r in jr.values() if r["kind"] == "bad_harmful")
    j_thr_good = sum((risk_of(r) if risk_of(r) is not None else 100) >= thr for r in jr.values() if r["kind"] == "good")
    assert j4["good_stop"] == st["good_stop"] == j_thr_good, "abstract says each stopped the same number of good calls"
    b = {r["item_id"]: r for r in j(T / "t0_balanced__test__sample300.json")["rows"]}
    c = {r["item_id"]: r for r in j(T / "cascade_aoai__test__sample300.json")["rows"]}
    f = {r["item_id"]: r for r in j(T / "cascade_fast__test__sample300.json")["rows"]}
    rel = lambda kind, src: sum(b[i]["kind"] == kind and b[i]["decision"] == "escalate" and src[i]["decision"] == "allow" for i in b)
    held = [i for i, r in b.items() if r["decision"] == "escalate" and r["kind"] in ("good", "bad_harmful")]
    f_blocked = [i for i in held if f[i]["decision"] == "block"]
    assert rel("good", f) == rel("bad_harmful", f) == 0
    pci = fr["paired_catch_differences"]["t0_strict - llm_judge_aoai@risk>=6"]["ci95_pp"]
    sgn = lambda x: (f"−{abs(int(-x + 0.5))}" if x < 0 else f"+{int(x + 0.5)}")
    words = {4: "four", 5: "five", 8: "eight", 11: "11"}
    out = [
        (ABSTRACT, f"yielded {dev['n'] + bal['n']:,} writes"),
        (ABSTRACT, f"({bal['n']} calls: {bal['good']} good, {bal['bad']} harmful, {full['n_rejected']} tool-rejected)"),
        (ABSTRACT, "Schema checks catch 0%"),
        (ABSTRACT, f"**{pc(v0['stop'], v0['bad'])} (95% CI {ci(v0['m']['ci95_cluster_bootstrap']['catch_harmful'])})** of harmful calls"),
        (ABSTRACT, f"blocks {pc(v0['fb'], v0['good'])} of good calls and holds {pc(v0['hold'], v0['good'])}"),
        (ABSTRACT, f"**{bal['stop']}/{bal['bad']}** harmful-labelled stops (**{pc(bal['stop'], bal['bad'])}; 95% CI "
                   f"{ci(bal['m']['ci95_cluster_bootstrap']['catch_harmful'])}**), comprising **{bal['hard']} blocks/{bal['stop'] - bal['hard']} holds**"),
        (ABSTRACT, f"**{bal['fb']}/{bal['good']} blocked ({pc(bal['fb'], bal['good'], 1)})**, **{bal['hold']}/{bal['good']} held ({pc(bal['hold'], bal['good'])})**"),
        (ABSTRACT, f"In-process retail p95: **{lat['configs']['t0_balanced']['wall_ms_p95']:.1f} ms** (median of 7 runs per call)"),
        (ABSTRACT, "It does not beat the untuned checker's score"),
        (ABSTRACT, f"gpt-4.1-mini stopped {j4['stop']}/{j4['bad']} harmful calls, or {j_thr}/{j4['bad']} at a test-selected threshold, "
                   f"versus strict Tier 0's {st['stop']}/{st['bad']}. Each stopped {st['good_stop']}/{st['good']} good calls."),
        (ABSTRACT, f"the paired 95% CI for strict minus thresholded judge is {sgn(pci[0])} to {sgn(pci[1])} points"),
        (ABSTRACT, f"gpt-4.1-mini released {rel('good', c)} good-labelled and {rel('bad_harmful', c)} harmful-labelled holds"),
        (ABSTRACT, f"Good-call holds fell {bs['hold']}/{bs['good']} to {ca['hold']}/{ca['good']}, but harmful catch fell "
                   f"{bs['stop']}/{bs['bad']} to {ca['stop']}/{ca['bad']}; good blocks stayed {ca['fb']}/{ca['good']}"),
        (ABSTRACT, f"about ${cost['cascade_aoai']['usd_per_guarded_call']:.5f}/sampled-call versus "
                   f"${cost['llm_judge_aoai']['usd_per_guarded_call']:.4f} for the judge (estimated)"),
        (ABSTRACT, f"Qwen3-1.7B converted {len(f_blocked)}/{len(held)} holds to blocks, including "
                   f"{sum(b[i]['kind'] == 'good' for i in f_blocked)} DB-good calls"),
        (ABSTRACT, f"found {words[n_user]} user-confirmed disagreements and {words[len(entity_ids)]} wrong-entity choices. "
                   f"All {words[len(entity_ids)]} wrong-entity calls still pass Tier 0"),
        (ABSTRACT, f"wrote {astra['n']} cases. After fixes, {astra['stop']}/{astra['bad']} bad calls were stopped (Wilson 95% CI "
                   f"{ci(astra['m']['ci95_wilson']['catch_rate'])}); {astra['fb']}/{astra['good']} good calls were blocked and "
                   f"{astra['hold']}/{astra['good']} held"),
        (readme, "re-run once"), (readme, "`a93e35a`"), (readme, "`74d2128`"), (readme, "**exploratory**"),
        (readme, "**task_id** clusters across both models"),
    ]
    assert synth["fb"] == 0
    for g, v in lat["configs"].items():  # latency claims come from the repeat-timed benchmark, not single-shot eval runs
        assert v["wall_ms_p95"] < 1.0 and v["cpu_ms_p95"] < 1.0, f"{g} benchmark p95 is not under 1 ms"
    stale = ["was run once on the frozen configs", "(model, task_id) clusters, 2,000 resamples"]
    for s_ in stale:
        assert s_ not in readme.read_text(), f"stale protocol text in README: {s_!r}"
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
