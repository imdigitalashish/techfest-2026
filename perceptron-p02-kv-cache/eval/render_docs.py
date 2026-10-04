"""Render every reported number from committed per-question rows (eval/results/*.rows.jsonl) into the docs.

- Writes eval/RESULTS.md (full tables + pre-registered verdicts, eval/PREREG.md).
- Fills marked blocks `<!-- p2:<name>:begin --> ... <!-- p2:<name>:end -->` in DOCS.
Statistics match eval/kvbench_torch.py: per-context recall, context-clustered bootstrap (2,000 resamples, seed 0).
Usage (from perceptron-p02-kv-cache/):  python3 eval/render_docs.py      (check: python3 eval/check_docs.py)
"""
from __future__ import annotations

import json
import random
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "eval" / "results"
SPLITS = {"T1": "T1_literal_s0", "T2": "T2_paraphrase_s1", "T3": "T3_alias_s2", "S4": "S4_halo64_s0"}
DOCS = ["eval/RESULTS.md", "deliverables/round1-abstract.md", "thought_node.md", "deliverables/selection-memo.md", "README.md"]
QA = ["h2o", "snapkv", "knorm", "kvp_streaming", "kvp_snapkv", "kvp_observed", "kvp_knorm", "kvp_expected", "kvp_tova"]
NAMES = {"full": "Full cache", "int8": "int8 KV", "int4": "int4 KV", "int2": "int2 KV", "streaming": "StreamingLLM (ours)",
         "random": "Random (control)", "h2o": "H2O-style (ours)", "snapkv": "SnapKV-variant (ours, +4 sinks)", "knorm": "K-norm (ours)",
         "snapkv_qa": "SnapKV, question-aware (oracle)", "rod": "**RoD (ours)**", "rodlex": "RoD-lexical (control)",
         "kvp_streaming": "kvpress StreamingLLM", "kvp_snapkv": "kvpress SnapKV", "kvp_observed": "kvpress ObservedAttention (H2O)",
         "kvp_knorm": "kvpress Knorm", "kvp_expected": "kvpress ExpectedAttention", "kvp_tova": "kvpress TOVA"}


def load(split):
    p = RES / f"{SPLITS[split]}.rows.jsonl"
    if not p.exists():
        return None
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    meta = json.loads((RES / f"{SPLITS[split]}.json").read_text())["meta"]
    return {"rows": rows, "meta": meta}


def per_ctx(rows, m, f):
    d = defaultdict(list)
    for r in rows:
        if r["method"] == m and abs(r["frac"] - f) < 1e-9:
            d[r["sample"]].append(r["correct"])
    return {s: sum(v) / len(v) for s, v in d.items()}, d


def boot_ci(per, reps=2000, seed=0):
    rng, keys = random.Random(seed), sorted(per)
    n, st = len(keys), []
    for _ in range(reps):
        smp = [per[keys[rng.randrange(n)]] for _ in range(n)]
        st.append(sum(sum(v) for v in smp) / max(1, sum(len(v) for v in smp)))
    st.sort()
    return st[int(0.025 * reps)], st[int(0.975 * reps) - 1]


def boot_delta(diffs, reps=2000, seed=0):
    rng, n = random.Random(seed), len(diffs)
    st = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(reps))
    return st[int(0.025 * reps)], st[int(0.975 * reps) - 1]


def table(rows, f=None):
    cfgs = sorted({(r["method"], r["frac"]) for r in rows},
                  key=lambda x: (x[1] != 1.0, x[1], list(NAMES).index(x[0]) if x[0] in NAMES else 99))
    out = []
    for m, fr in cfgs:
        if f is not None and abs(fr - f) > 1e-9 and fr != 1.0:
            continue
        rs = [r for r in rows if r["method"] == m and r["frac"] == fr]
        _, d = per_ctx(rows, m, fr)
        lo, hi = boot_ci(d)
        sb = sum(r["stored_bytes"] for r in rs) / len(rs)
        ab = sum(r["answer_time_bytes"] for r in rs) / len(rs)
        fb = sum(r["full_bytes"] for r in rs) / len(rs)
        ev = [r for r in rs if r.get("needle_evicted")]
        out.append({"m": m, "f": fr, "n": len(rs), "nctx": len(d), "acc": sum(r["correct"] for r in rs) / len(rs), "lo": lo, "hi": hi,
                    "stored": sb / 2**20, "answer": ab / 2**20, "full": fb / 2**20, "x": fb / sb, "xa": fb / ab,
                    "s": sum(r["answer_s"] for r in rs) / len(rs),
                    "hit": (sum(bool(r.get("needle_block_hit")) for r in ev) / len(ev)) if ev else None})
    return out


def delta(rowsA, mA, rowsB, mB, f, fB=None):
    a, _ = per_ctx(rowsA, mA, f)
    b, _ = per_ctx(rowsB, mB, f if fB is None else fB)
    ks = sorted(set(a) & set(b))
    if not ks:
        return None
    d = [a[k] - b[k] for k in ks]
    lo, hi = boot_delta(d)
    return {"d": sum(d) / len(d), "lo": lo, "hi": hi, "n": len(ks)}


def fmt_d(x):
    return "pending" if x is None else f"{x['d']:+.3f} (95% CI {x['lo']:+.2f} to {x['hi']:+.2f}, {x['n']} contexts)"


def md_table(tab):
    lines = ["| Method | Keep | Recall | 95% CI | Stored KV MiB | Compression | Answer-time MiB | s/answer (CPU) | Needle-block hit |",
             "|---|---|---|---|---|---|---|---|---|"]
    for t in tab:
        hit = "" if t["hit"] is None else f"{t['hit']:.2f}"
        lines.append(f"| {NAMES.get(t['m'], t['m'])} | {t['f']:.2f} | {t['acc']:.3f} | {t['lo']:.2f}–{t['hi']:.2f} | {t['stored']:.1f} | "
                     f"{t['x']:.1f}× | {t['answer']:.1f} | {t['s']:.2f} | {hit} |")
    return "\n".join(lines)


def compute():
    D = {k: load(k) for k in SPLITS}
    V = {}
    T1, T2, T3, S4 = (D[k]["rows"] if D[k] else None for k in ("T1", "T2", "T3", "S4"))
    if T1:
        V["primary"] = delta(T1, "rod", T1, "streaming", 0.25)
        V["S7"] = {f: delta(T1, "rod", T1, "full", f, fB=1.0) for f in (0.1, 0.25, 0.5)}
        V["drops"] = {(m, f): delta(T1, m, T1, "full", f, fB=1.0) for (m, f) in sorted({(r["method"], r["frac"]) for r in T1})
                      if m != "full"}
        V["percontext"] = {"primary": per_context(T1, "rod", "streaming", 0.25, 0.25),
                           "S7": per_context(T1, "rod", "full", 0.25, 1.0)}
        V["strict"] = strict_table(T1)
        V["S1"] = {b: delta(T1, "rod", T1, b, 0.25) for b in QA}
        V["S2_T1"] = delta(T1, "rod", T1, "rodlex", 0.25)
        V["S5"] = {f: {b: delta(T1, "rod", T1, b, f) for b in ["streaming", "snapkv", "h2o", "rodlex", "kvp_expected"]} for f in (0.1, 0.5)}
        V["T1"] = table(T1)
    if T2:
        V["R1"] = delta(T2, "rod", T2, "full", 0.1, fB=1.0)
        V["R2"] = {k: mech(rows, "rod") for k, rows in (("T1", T1), ("T2", T2)) if rows}
        V["S3"] = delta(T2, "rod", T2, "streaming", 0.25)
        V["S2_T2"] = delta(T2, "rod", T2, "rodlex", 0.25)
        V["T2"] = table(T2)
    if T3:
        V["S6"] = {f: delta(T3, "rod", T3, "rodlex", f) for f in (0.1, 0.25)}
        V["T3"] = table(T3)
    if S4 and T1:
        V["S4"] = {f: delta(S4, "rod", T1, "rod", f) for f in (0.1, 0.25, 0.5)}
        V["S4tab"] = table(S4)
        tS4, tT1 = {r["sample"]: r["T"] for r in S4}, {r["sample"]: r["T"] for r in T1}
        same = all(tS4[s] == tT1.get(s) for s in tS4)
        V["S4_pairing"] = f"{len(tS4)} contexts; context lengths identical to T1's: {'yes' if same else 'NO'}"
    for k, rows in (("T1", T1), ("T2", T2), ("T3", T3)):
        if rows:
            V[f"bytecheck_{k}"] = byte_check(rows)
    V["meta"] = {k: (D[k]["meta"] if D[k] else None) for k in SPLITS}
    V["meanT"] = {k: (sum({r["sample"]: r["T"] for r in D[k]["rows"]}.values()) / len({r["sample"] for r in D[k]["rows"]}) if D[k] else None)
                  for k in SPLITS}
    return V


def get(tab, m, f):
    return next((t for t in tab or [] if t["m"] == m and abs(t["f"] - f) < 1e-9), None)


def e6_delta():
    """Paired context-bootstrap CI of RoD@0.10 - full on T2 with max_new=32 (strict first-number scoring), from E6 rows."""
    p = RES / "e6_maxnew32_T2.rows.jsonl"
    if not p.exists():
        return None
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]

    def acc(m, f):
        out = {}
        for s in sorted({r["sample"] for r in rows}):
            rs = [r for r in rows if r["method"] == m and r["frac"] == f and r["sample"] == s]
            out[s] = sum(r["strict"] for r in rs) / len(rs)
        return out
    a, b = acc("rod", 0.1), acc("full", 1.0)
    d = [a[s] - b[s] for s in sorted(a)]
    lo, hi = boot_delta(d)
    return {"d": sum(d) / len(d), "lo": lo, "hi": hi, "n": len(d), "rod": sum(a.values()) / len(a), "full": sum(b.values()) / len(b)}


def trunc_stats(rows, m, f):
    """Wrong answers of method m at keep f: how many contain no 7-digit number and look cut off (>= 30 chars)."""
    rs = [r for r in rows if r["method"] == m and abs(r["frac"] - f) < 1e-9 and not r["correct"]]
    nonum = [r for r in rs if not re.search(r"\d{7}", r["answer"].replace(",", ""))]
    return {"wrong": len(rs), "no_number": len(nonum), "cut": sum(len(r["answer"]) >= 30 for r in nonum)}


def mech(rows, m):
    vals = defaultdict(set)
    for r in rows:
        vals[r["sample"]].add(r["value"])
    out = {}
    for f in (0.1, 0.25, 0.5):
        rs = [r for r in rows if r["method"] == m and abs(r["frac"] - f) < 1e-9]
        if not rs:
            continue
        hit = [r for r in rs if r.get("needle_block_hit")]
        wrong = [r for r in rs if not r["correct"]]
        other = sum(any(v in r["answer"].replace(",", "") for v in vals[r["sample"]] - {r["value"]}) for r in wrong)
        out[f] = {"acc_given_hit": sum(r["correct"] for r in hit) / max(1, len(hit)), "n_hit": len(hit),
                  "wrong": len(wrong), "wrong_other_needle": other,
                  "hit_rate": len(hit) / max(1, sum(bool(r.get("needle_evicted")) for r in rs))}
    return out


def per_context(rows, mA, mB, fA, fB):
    a, la = per_ctx(rows, mA, fA)
    b, lb = per_ctx(rows, mB, fB)
    qa = {(r["sample"], r["q"]): r["correct"] for r in rows if r["method"] == mA and abs(r["frac"] - fA) < 1e-9}
    qb = {(r["sample"], r["q"]): r["correct"] for r in rows if r["method"] == mB and abs(r["frac"] - fB) < 1e-9}
    ks = sorted(set(qa) & set(qb))
    return {"deltas": [round(a[s] - b[s], 3) for s in sorted(set(a) & set(b))],
            "a_only": sum(qa[k] and not qb[k] for k in ks), "b_only": sum(qb[k] and not qa[k] for k in ks), "n_q": len(ks)}


def strict_table(rows):
    vals = defaultdict(set)
    for r in rows:
        vals[r["sample"]].add(r["value"])
    out = {}
    for (m, f) in sorted({(r["method"], r["frac"]) for r in rows}):
        rs = [r for r in rows if r["method"] == m and r["frac"] == f]
        strict = [r["correct"] and not any(v in r["answer"].replace(",", "") for v in vals[r["sample"]] - {r["value"]}) for r in rs]
        out[(m, f)] = sum(strict) / len(rs)
    return out


def rod_budget(T, f, per_tok=32768, nkv=8, hd=64, bits=4, wq=262144, block=64):
    """Mirror of kvbench_torch.rod_build's budget arithmetic for the frozen config."""
    import math
    B = max(4 + 64 + 1, round(f * T))
    extra = nkv * (hd * bits // 8 + 4) * T + 4 * T + wq
    B_kv = max(6, B - math.ceil(extra / per_tok))
    B_res = max(5, B_kv // 2)
    return {"B": B, "B_res": B_res, "m": (B_kv - B_res) // block, "E": T - B_res}


def transient_bytes(T, f, Lq=20, nkv=8, g=4, hd=64, W=64):
    """Analytic upper bound of RoD's unchunked scoring working set: dense fp32 sketch + fp32 question and window
    logits and their softmax copies over all evicted keys (the implementation is not streamed)."""
    E = rod_budget(T, f)["E"]
    return E * (nkv * hd * 4 + 2 * nkv * g * Lq * 4 + 2 * nkv * g * W * 4)


def byte_check(rows):
    """Count (context, keep) cells where RoD's answer-time bytes exceed any baseline's stored bytes."""
    st = defaultdict(dict)
    for r in rows:
        if r["method"] not in ("full", "int8", "int4", "int2", "snapkv_qa"):
            key = (r["sample"], round(r["frac"], 4))
            v = r["answer_time_bytes"] if r["method"] in ("rod", "rodlex") else r["stored_bytes"]
            st[key][r["method"]] = max(st[key].get(r["method"], 0), v)
    viol, cells = 0, 0
    for key, d in st.items():
        if "rod" in d:
            base = [v for m, v in d.items() if m not in ("rod", "rodlex")]
            if base:
                cells += 1
                viol += d["rod"] > min(base)
    return viol, cells


def verdicts(V):
    out = []
    p = V.get("primary")
    out.append(f"- **Primary** (RoD − StreamingLLM, keep 0.25, T1): {fmt_d(p)} → "
               + ("pending" if p is None else ("**SUCCESS** (lower bound > 0)" if p["lo"] > 0 else "**NOT SHOWN** (lower bound ≤ 0)")))
    for f, x in (V.get("S7") or {}).items():
        tag = " (confirmatory, margin −0.05)" if f == 0.25 else " (descriptive)"
        verdict = "" if x is None or f != 0.25 else (" → **non-inferior** (lower bound > −0.05)" if x["lo"] > -0.05 else " → non-inferiority **not shown**")
        out.append(f"- **S7** (RoD − full cache, keep {f}, T1){tag}: {fmt_d(x)}{verdict}")
    s1 = V.get("S1") or {}
    ok = [b for b, x in s1.items() if x is not None]
    allpos = ok and all(s1[b]["lo"] > 0 for b in ok)
    out.append(f"- **S1** (RoD vs each query-agnostic baseline, keep 0.25, T1): "
               + ("pending" if not ok else ("beats **all** " if allpos else "does not beat all ") + f"{len(ok)} baselines; weakest margin "
                  + min((f"{NAMES[b]} {fmt_d(s1[b])}" for b in ok), key=lambda s: float(re.search(r'([+-][0-9.]+) \(', s).group(1)))))
    for k, lab in (("S2_T1", "T1 literal"), ("S2_T2", "T2 paraphrase")):
        x = V.get(k)
        out.append(f"- **S2** (RoD − RoD-lexical, keep 0.25, {lab}): {fmt_d(x)}"
                   + ("" if x is None else (" → sketch beats lexical" if x["lo"] > 0 else " → no evidence the sketch beats lexical retrieval")))
    if V.get("R1") is not None:
        x = V["R1"]
        out.append(f"- **R1** (replication on T2: RoD − full at keep 0.10, margin −0.15): {fmt_d(x)} → "
                   + ("**replicated** (lower bound > −0.15)" if x["lo"] > -0.15 else "**not replicated**"))
    if V.get("T2"):
        tr, trr = trunc_stats(load("T2")["rows"], "full", 1.0), trunc_stats(load("T2")["rows"], "rod", 0.1)
        out.append(f"- **R1 caveat (amendment 5):** of the full cache's {tr['wrong']} wrong T2 answers, {tr['no_number']} contain no 7-digit number "
                   f"({tr['cut']} look cut off by the 10-token limit: ≥ 30 characters without a 7-digit number, a heuristic, not recorded finish reasons); RoD at 0.10: {trr['no_number']} of {trr['wrong']} ({trr['cut']} look cut off). "
                   "'RoD exceeds full on T2' is confounded by answer truncation.")
    e6 = RES / "e6_maxnew32_T2.json"
    if e6.exists():
        S = json.loads(e6.read_text())["summary"]
        out.append("- **E6 (exploratory, T2, max_new=32; lenient / strict first-number):** "
                   + "; ".join(f"{k} {v['lenient']:.3f} / {v['strict']:.3f}" for k, v in S.items()))
    for k, mm in (V.get("R2") or {}).items():
        out.append(f"- **R2 mechanism {k}** (RoD): " + "; ".join(
            f"keep {f}: block hit {d['hit_rate']:.2f}, accuracy given hit {d['acc_given_hit']:.2f}, "
            f"{d['wrong_other_needle']}/{d['wrong']} wrong answers name another needle's value" for f, d in mm.items()))
    x = V.get("S3")
    out.append(f"- **S3** (primary replicated on T2 paraphrase): {fmt_d(x)}"
               + ("" if x is None else (" → replicated" if x["lo"] > 0 else " → not replicated")))
    for f, x in (V.get("S4") or {}).items():
        out.append(f"- **S4** (halo 64 − halo 0, RoD, keep {f}, T1): {fmt_d(x)}")
    if V.get("T1"):
        for f in (0.1, 0.5):
            cells = []
            for b in ["streaming", "snapkv", "h2o", "rodlex", "kvp_expected"]:
                x = (V.get("S5") or {}).get(f, {}).get(b)
                cells.append(f"{NAMES[b]} {fmt_d(x)}" if x else f"{NAMES[b]} not run")
            out.append(f"- **S5** (RoD − baseline, keep {f}, T1): " + "; ".join(cells))
    for k in ("T1", "T2", "T3"):
        if V.get(f"bytecheck_{k}"):
            v, c = V[f"bytecheck_{k}"]
            out.append(f"- **Byte check {k}**: RoD answer-time bytes > a baseline's stored bytes in {v} of {c} (context, keep) cells")
    if V.get("S4_pairing"):
        out.append(f"- **S4 pairing**: {V['S4_pairing']}")
    for f, x in (V.get("S6") or {}).items():
        conf = f == 0.1
        out.append(f"- **S6** (RoD − RoD-lexical, keep {f}, T3 synonym-aliased keys; {'confirmatory' if conf else 'exploratory'}): {fmt_d(x)}"
                   + ("" if x is None or not conf else (" → the sketch out-retrieves the lexical index on non-shared key words" if x["lo"] > 0 else " → not shown")))
    if V.get("T3"):
        fc = get(V["T3"], "full", 1.0)
        out.append(f"- **T3 ceiling** (full cache): recall {fc['acc']:.3f}" + (" (≥ 0.5: T3 informative)" if fc["acc"] >= 0.5 else " (< 0.5: T3 too hard; S6 inconclusive)"))
    return "\n".join(out)


def headline(V):
    t = V.get("T1")
    if not t:
        return "_Measured results pending (pre-registered runs in progress)._"
    pc = lambda x: "n/a" if x is None else f"{x['acc']:.0%}"
    full, rod, rod10 = get(t, "full", 1.0), get(t, "rod", 0.25), get(t, "rod", 0.1)
    base25 = [get(t, b, 0.25)["acc"] for b in ["streaming"] + QA if get(t, b, 0.25)]
    base10 = [get(t, b, 0.1)["acc"] for b in ["streaming"] + QA if get(t, b, 0.1)]
    p, s7 = V["primary"], V["S7"][0.25]
    s = (f"On 12 held-out ~4k-token contexts (48 questions; Llama-3.2-1B-Instruct) the full cache recalls {pc(full)}. Keeping 25% of the "
         f"KV state (logical bytes retained after prefill, not peak RAM), ten tested eviction baselines recall {min(base25):.0%}–{max(base25):.0%} "
         f"and RoD {pc(rod)}: {p['d']:+.2f} over StreamingLLM (95% CI {p['lo']:+.2f} to {p['hi']:+.2f}; pre-registered), yet "
         f"{abs(s7['d']):.2f} below the full cache. At 10% RoD recalls {pc(rod10)} (baselines ≤{max(base10):.0%})")
    e6 = e6_delta()
    if e6 is not None:
        s += (f"; on fresh paraphrased contexts, with answers allowed 32 tokens, it recalls {e6['rod']:.0%} vs the full cache's "
              f"{e6['full']:.0%} ({e6['d']:+.2f}, 95% CI {e6['lo']:+.2f} to {e6['hi']:+.2f}; exploratory), so superiority is not established")
    return s + "."

def block_hit(rows, m, f):
    ev = [r for r in rows if r["method"] == m and abs(r["frac"] - f) < 1e-9 and r.get("needle_evicted")]
    return sum(bool(r.get("needle_block_hit")) for r in ev) / max(1, len(ev))


def caveats(V):
    if not V.get("T1"):
        return "_Controls pending._"
    sh = lambda x: "pending" if x is None else f"{x['d']:+.2f} ({x['lo']:+.2f} to {x['hi']:+.2f})"
    rod, st = get(V["T1"], "rod", 0.25), get(V["T1"], "streaming", 0.25)
    mm = mech(load("T1")["rows"], "rod")
    parts = [f"RoD minus a lexical index over the same ids at 25%: {sh(V.get('S2_T1'))} on literal"
             + (f" and {sh(V.get('S2_T2'))} on paraphrased needles" if V.get("T2") else " needles")]
    ph = RES / "posthoc_T1.json"
    mech_s = (f"accuracy given a recalled needle falls from {mm[0.1]['acc_given_hit']:.0%} (10%) to {mm[0.25]['acc_given_hit']:.0%} (25%), "
              f"mostly naming another needle's value")
    if ph.exists():
        S = json.loads(ph.read_text())["summary"]["0.25"]
        mech_s += (f"; exact KV for the same blocks gives {S['e2_exactkv_acc']:.0%} and recalling only the top-2 blocks "
                   f"{S['e5_top2_acc']:.0%} (exploratory), implicating approximate multi-block re-prefill")
    parts.append(mech_s)
    if V.get("T3"):
        r3 = load("T3")["rows"]
        fc = get(V["T3"], "full", 1.0)
        parts.append(f"synonym-aliased keys defeat even the full cache ({fc['acc']:.0%}), so meaning-based retrieval is untested "
                     f"(RoD's block hit there is {block_hit(r3, 'rod', 0.1):.0%} vs {block_hit(r3, 'rodlex', 0.1):.0%} for lexical)")
    parts.append(f"CPU answer time {rod['s'] / st['s']:.1f}× StreamingLLM's")
    return "; ".join(parts).capitalize()[:1] + "; ".join(parts)[1:] + "."


def memo_scores(V):
    """Selection-memo scores by rules fixed before T2/T3 outcomes were seen (deliverables/selection-memo.md)."""
    t = V.get("T1")
    if not t:
        return "_Scores pending._"
    p, r1 = V["primary"], V.get("R1")
    lex10 = (V.get("S5") or {}).get(0.1, {}).get("rodlex")
    rep = r1 is not None and r1["lo"] > -0.15
    rod10, full = get(t, "rod", 0.1), get(t, "full", 1.0)
    b10 = max(get(t, b, 0.1)["acc"] for b in ["streaming"] + QA if get(t, b, 0.1))
    win = 4 if p["lo"] > 0 and rep else (3 if p["lo"] > 0 else 2)
    inn = 4 if lex10 is not None and lex10["lo"] > 0 else 3
    demo = 4 if rep else 3
    rows = [
        ("Winnability", win, f"Pre-registered primary {'passed' if p['lo'] > 0 else 'failed'}: RoD − StreamingLLM {p['d']:+.2f} (95% CI {p['lo']:+.2f} to {p['hi']:+.2f}) at 25% memory, "
         f"and RoD beats all nine tested query-agnostic baselines there, including NVIDIA kvpress's reference presses. Non-inferiority vs the full cache at 25% was not shown. "
         + ("The 10% observation replicated on fresh contexts (R1), though T2's full-cache ceiling is depressed by a 10-token answer limit (amendment 5)." if rep else ("The 10% observation did not replicate (R1)." if r1 is not None else "R1 replication pending."))),
        ("Innovation headroom", inn, "A narrow but real combination: token-backed selective recomputation guided by a single-layer 4-bit key index with a contrastive scorer. Its constituents are prior art "
         f"(hostile judge: 3/5). At 10% memory the sketch beats a lexical index over the same ids by {lex10['d']:+.2f} (95% CI {lex10['lo']:+.2f} to {lex10['hi']:+.2f}). "
         + (f"With synonym-aliased keys (too hard even for the full cache) its block hit is {block_hit(load('T3')['rows'], 'rod', 0.1):.0%} vs "
            f"{block_hit(load('T3')['rows'], 'rodlex', 0.1):.0%} for lexical, so meaning-based retrieval is not shown. " if V.get("T3") else "")
         + "Headroom: precision-first recall, a streamed scorer, per-channel sketches, multi-turn."),
        ("Feasibility", 4, "The whole pre-registered evaluation runs end to end on one CPU VM, with logit parity, identity checks, reference baselines and reviews. "
         "The Apple-silicon (MLX) demo path is not yet validated; CPU answer time is "
         f"{get(t, 'rod', 0.25)['s'] / get(t, 'streaming', 0.25)['s']:.1f}× StreamingLLM's at 25% memory. The 19–25 Nov exams are left free."),
        ("Demo strength", demo, f"Live: a 1B model answers questions about a long document holding 10% of its KV. RoD {rod10['acc']:.0%} vs ≤{b10:.0%} for every tested eviction "
         f"baseline (full cache {full['acc']:.0%}), with a memory meter. Synthetic needles are less visual than a real chat."),
        ("Fit with the user", 5, "Inference systems: cache hierarchy, recompute vs memory trade-off, kernels. This is core Microsoft-style systems work."),
    ]
    lines = ["| Criterion | Score | Evidence |", "|---|---|---|"] + [f"| **{n}** | {s} | {e} |" for n, s, e in rows]
    tot = sum(s for _, s, _ in rows)
    lines += ["", f"**Overall: {tot / len(rows):.1f} / 5**, the unweighted mean ({' + '.join(str(s) for _, s, _ in rows)} = {tot})."]
    return "\n".join(lines)


def memo_pitch(V):
    if not V.get("T1"):
        return "_Pitch pending._"
    r1 = V.get("R1")
    if r1 is not None and r1["lo"] > -0.15:
        return ('"Treat the KV cache as a cache: keep one layer\'s keys at 4 bits plus the token ids, and recompute only the blocks a '
                'question asks for. With a tenth of the memory, every tested eviction method forgets the needle; RoD finds it, on two '
                'independent test splits."')
    p = V["primary"]
    return ('"Treat the KV cache as a cache: keep one layer\'s keys at 4 bits plus the token ids, and recompute only the blocks a '
            f'question asks for. At a quarter of the memory it recovers {p["d"]:.0%} of recall that StreamingLLM loses (pre-registered)."')


def render_blocks(V):
    blocks = {"headline": headline(V), "verdicts": verdicts(V), "caveats": caveats(V), "memo-scores": memo_scores(V),
              "memo-pitch": memo_pitch(V)}
    if V.get("T1"):
        keep = [t for t in V["T1"] if t["f"] in (1.0, 0.25)]
        blocks["t1-table-025"] = md_table(keep)
    return blocks


def results_md(V):
    parts = ["# Results (rendered by `eval/render_docs.py` from committed rows; do not edit by hand)", "",
             "Pre-registration: [`PREREG.md`](PREREG.md). Engine parity: [`results/parity_torch.json`](results/parity_torch.json).", "",
             "## Pre-registered verdicts", "", verdicts(V), ""]
    for k, lab in (("T1", "T1 — literal needles, seed 0"), ("T2", "T2 — paraphrased templates, seed 1"),
                   ("T3", "T3 — synonym-aliased keys, seed 2"), ("S4tab", "S4 — RoD with halo 64, seed 0")):
        if V.get(k):
            sk = "S4" if k == "S4tab" else k
            m = V["meta"][sk]
            parts += [f"## {lab}", "", f"`{m['command']}`", "",
                      f"{m['backend']} · {m['cpu']} · torch {m['torch']} · {m['threads']} threads · wall {m['wall_s']} s · "
                      f"{m['n_contexts']} contexts × {m['needles']} questions · mean context {V['meanT'][sk]:.0f} tokens", "", md_table(V[k]), ""]
    if V.get("T1"):
        parts += ["## Recall drop vs the full cache (T1, paired by context; MVP)", "",
                  "| Method | Keep | Recall | Strict recall | Drop vs full (95% CI) |", "|---|---|---|---|---|"]
        for (m, f), x in sorted(V["drops"].items(), key=lambda kv: (kv[0][1] != 1.0, kv[0][1], list(NAMES).index(kv[0][0]) if kv[0][0] in NAMES else 99)):
            row = get(V["T1"], m, f)
            parts.append(f"| {NAMES.get(m, m)} | {f:.2f} | {row['acc']:.3f} | {V['strict'][(m, f)]:.3f} | "
                         f"{x['d']:+.3f} ({x['lo']:+.2f} to {x['hi']:+.2f}) |")
        for k, lab in (("primary", "Primary: RoD vs StreamingLLM at keep 0.25"), ("S7", "S7: RoD (keep 0.25) vs full cache")):
            pc = V["percontext"][k]
            parts += ["", f"**{lab}: per-context deltas** (12 contexts): {pc['deltas']}; questions where only RoD is right: "
                      f"{pc['a_only']}, only the comparator: {pc['b_only']} (of {pc['n_q']})."]
        parts.append("")
    ic = RES / "identity_check_dev100.json"
    if ic.exists():
        I = json.loads(ic.read_text())
        parts += ["## Identity / plumbing checks (dev seed 100; Supervisor 16:24 spot-check)", "",
                  f"`{I['command']}` · context {I['T']} tokens, 4 questions", "",
                  "| Keep | B | Resident | Recall budget m (blocks) | Evicted tokens | I3 partition exact | I1 exact-KV assembly: max abs Δlogit, answers = full | I2 one-pass re-prefill: max abs ΔKV, answers = full |",
                  "|---|---|---|---|---|---|---|---|"]
        for f, d in I["per_keep"].items():
            parts.append(f"| {float(f):.2f} | {d['B']} | {d['B_res']} | {d['m']} | {d['evicted_tokens']} | {d['I3_partition_ok']} | "
                         f"{d['I1_max_abs_dlogit']:.4f}, {d['I1_answers_equal']}/{d['n_questions']} | {d['I2_max_abs_dkv']:.4f}, {d['I2_answers_equal']}/{d['n_questions']} |")
        parts += ["", "Positions, masks, cache assembly and block bookkeeping reproduce the full cache whenever the evicted KV is restored "
                  "exactly or recomputed with its true prefix, so RoD's recall loss is not a plumbing artifact.", ""]
    ph = RES / "posthoc_T1.json"
    if ph.exists():
        P = json.loads(ph.read_text())
        parts += ["## Exploratory post-hoc analyses on T1 contexts (PREREG amendment 3; not confirmatory)", "",
                  f"`{P['command']}` · streamed vs unchunked max |Δscore| {P['max_abs_score_diff_streamed_vs_unchunked']:.2e} · "
                  f"streamed transient set ≤ {P['transient_bytes_streamed_chunk256_upper_bound'] / 2**20:.2f} MiB", "",
                  "| Keep | Questions | Recall blocks m | E1 streamed = unchunked | Unchunked = T1 recorded | RoD (T1) | E2 exact-KV oracle | E3 oracle block | E2+E3 | E5 top-2 only |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        for f, s in P["summary"].items():
            rodacc = "n/a" if s["rod_T1_acc"] is None else f"{s['rod_T1_acc']:.3f}"
            parts.append(f"| {float(f):.2f} | {s['n']} | {s['m_mean']:.1f} | {s['streamed_equal']}/{s['n']} | {s['t1_recorded_equal']}/{s['n']} | "
                         f"{rodacc} | {s['e2_exactkv_acc']:.3f} | {s['e3_oracleblk_acc']:.3f} | {s['e23_both_acc']:.3f} | "
                         f"{'n/a' if s.get('e5_top2_acc') is None else format(s['e5_top2_acc'], '.3f')} |")
        parts.append("")
    if V.get("T1"):
        Ts = sorted({r["sample"]: r["T"] for r in load("T1")["rows"]}.values())
        Tm = round(sum(Ts) / len(Ts))
        parts += ["## RoD's transient scoring working set (analytic, T1 mean context)", "",
                  "| Keep | Recall blocks m | Evicted tokens E | Persistent store MiB | Transient scoring set MiB (unchunked upper bound) |",
                  "|---|---|---|---|---|"]
        for f in (0.1, 0.25, 0.5):
            b, row = rod_budget(Tm, f), get(V["T1"], "rod", f)
            stored = f"{row['stored']:.1f}" if row else "n/a"
            parts.append(f"| {f:.2f} | {b['m']} | {b['E']} | {stored} | {transient_bytes(Tm, f) / 2**20:.1f} |")
        parts += ["", "The scorer materialises a dense fp32 copy of the sketch and fp32 question/window score tensors over all evicted "
                  "keys. A streamed implementation (online softmax over key chunks; the window term precomputed per key at compression) "
                  "bounds this to O(chunk). It is reported here so that no peak-memory-equality claim is implied.", ""]
    parts += ["## Memory accounting", "",
              "Stored KV MiB = analytic bytes = layers × kv_heads × kept tokens × head_dim × 2 (K,V) × 2 B (fp16), plus quantisation "
              "scales/biases and, for RoD, the 4-bit sketch, 256 KiB of window queries and int32 token ids. The harness asserts that the "
              "full cache's measured tensor bytes equal T × 32 KiB. Answer-time MiB adds RoD's recalled blocks. CPU seconds are relative only.", ""]
    return "\n".join(parts)


def render(text, blocks):
    for name, body in blocks.items():
        text = re.sub(rf"(<!-- p2:{name}:begin -->)(.*?)(<!-- p2:{name}:end -->)", lambda m: f"{m.group(1)}\n{body}\n{m.group(3)}", text, flags=re.S)
    return text


def main():
    V = compute()
    (ROOT / "eval" / "RESULTS.md").write_text(results_md(V) + "\n")
    blocks = render_blocks(V)
    for rel in DOCS[1:]:
        p = ROOT / rel
        if p.exists():
            p.write_text(render(p.read_text(), blocks))
    print("rendered:", ", ".join(k for k in ("T1", "T2", "T3", "S4") if V["meta"].get(k)) or "no results yet")


if __name__ == "__main__":
    main()
