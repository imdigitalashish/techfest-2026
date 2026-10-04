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
DOCS = ["eval/RESULTS.md", "deliverables/round1-abstract.md", "thought_node.md", "deliverables/selection-memo.md"]
QA = ["h2o", "snapkv", "knorm", "kvp_streaming", "kvp_snapkv", "kvp_observed", "kvp_knorm", "kvp_expected", "kvp_tova"]
NAMES = {"full": "Full cache", "int8": "int8 KV", "int4": "int4 KV", "int2": "int2 KV", "streaming": "StreamingLLM (ours)",
         "random": "Random (control)", "h2o": "H2O-style (ours)", "snapkv": "SnapKV-style (ours)", "knorm": "K-norm (ours)",
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
        V["S1"] = {b: delta(T1, "rod", T1, b, 0.25) for b in QA}
        V["S2_T1"] = delta(T1, "rod", T1, "rodlex", 0.25)
        V["S5"] = {f: {b: delta(T1, "rod", T1, b, f) for b in ["streaming", "snapkv", "h2o", "rodlex", "kvp_expected"]} for f in (0.1, 0.5)}
        V["T1"] = table(T1)
    if T2:
        V["S3"] = delta(T2, "rod", T2, "streaming", 0.25)
        V["S2_T2"] = delta(T2, "rod", T2, "rodlex", 0.25)
        V["T2"] = table(T2)
    if T3:
        V["S6"] = {f: delta(T3, "rod", T3, "rodlex", f) for f in (0.1, 0.25)}
        V["T3"] = table(T3)
    if S4 and T1:
        V["S4"] = {f: delta(S4, "rod", T1, "rod", f) for f in (0.1, 0.25, 0.5)}
        V["S4tab"] = table(S4)
    V["meta"] = {k: (D[k]["meta"] if D[k] else None) for k in SPLITS}
    V["meanT"] = {k: (sum({r["sample"]: r["T"] for r in D[k]["rows"]}.values()) / len({r["sample"] for r in D[k]["rows"]}) if D[k] else None)
                  for k in SPLITS}
    return V


def get(tab, m, f):
    return next((t for t in tab or [] if t["m"] == m and abs(t["f"] - f) < 1e-9), None)


def verdicts(V):
    out = []
    p = V.get("primary")
    out.append(f"- **Primary** (RoD − StreamingLLM, keep 0.25, T1): {fmt_d(p)} → "
               + ("pending" if p is None else ("**SUCCESS** (lower bound > 0)" if p["lo"] > 0 else "**NOT SHOWN** (lower bound ≤ 0)")))
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
    x = V.get("S3")
    out.append(f"- **S3** (primary replicated on T2 paraphrase): {fmt_d(x)}"
               + ("" if x is None else (" → replicated" if x["lo"] > 0 else " → not replicated")))
    for f, x in (V.get("S4") or {}).items():
        out.append(f"- **S4** (halo 64 − halo 0, RoD, keep {f}, T1): {fmt_d(x)}")
    for f, x in (V.get("S6") or {}).items():
        out.append(f"- **S6** (RoD − RoD-lexical, keep {f}, T3 synonym-aliased keys): {fmt_d(x)}"
                   + ("" if x is None else (" → sketch retrieves by meaning where lexical cannot" if x["lo"] > 0 else " → not shown")))
    if V.get("T3"):
        fc = get(V["T3"], "full", 1.0)
        out.append(f"- **T3 ceiling** (full cache): recall {fc['acc']:.3f}" + (" (≥ 0.5: T3 informative)" if fc["acc"] >= 0.5 else " (< 0.5: T3 too hard; S6 inconclusive)"))
    return "\n".join(out)


def headline(V):
    t = V.get("T1")
    if not t:
        return "_Measured results pending (pre-registered runs in progress)._"
    pc = lambda x: "n/a" if x is None else f"{x['acc']:.0%}"
    full, rod, st = get(t, "full", 1.0), get(t, "rod", 0.25), get(t, "streaming", 0.25)
    exp, snap = get(t, "kvp_expected", 0.25), get(t, "kvp_snapkv", 0.25)
    p = V["primary"]
    return (f"On 12 held-out ~4k-token contexts (48 questions; Llama-3.2-1B-Instruct), the full cache recalls {pc(full)} of needles. "
            f"At a quarter of the KV memory, StreamingLLM recalls {pc(st)}, kvpress SnapKV {pc(snap)} and kvpress ExpectedAttention "
            f"{pc(exp)}; Recall-on-Demand recalls {pc(rod)} (95% CI {rod['lo']:.0%}–{rod['hi']:.0%}) while *storing* "
            f"{rod['x']:.1f}× less KV than the full cache: a pre-registered gain of {p['d']:+.2f} recall over StreamingLLM "
            f"(95% CI {p['lo']:+.2f} to {p['hi']:+.2f}).")


def caveats(V):
    if not V.get("T1"):
        return "_Controls pending._"
    sh = lambda x: "pending" if x is None else f"{x['d']:+.2f} (95% CI {x['lo']:+.2f} to {x['hi']:+.2f})"
    rod, st = get(V["T1"], "rod", 0.25), get(V["T1"], "streaming", 0.25)
    parts = [f"RoD minus a lexical index over the same ids, {sh(V.get('S2_T1'))}"]
    if V.get("T2"):
        parts.append(f"paraphrased templates, RoD minus StreamingLLM {sh(V.get('S3'))}")
    if V.get("T3"):
        fc = get(V["T3"], "full", 1.0)
        parts.append(f"synonym-aliased keys (full-cache ceiling {fc['acc']:.0%}), RoD minus lexical {sh((V.get('S6') or {}).get(0.25))}")
    if V.get("S4"):
        parts.append(f"64 tokens of recompute context, {sh(V['S4'].get(0.25))}")
    parts.append(f"CPU time per answer {rod['s'] / st['s']:.1f}× StreamingLLM's")
    return "At 25% memory: " + "; ".join(parts) + "."


def render_blocks(V):
    blocks = {"headline": headline(V), "verdicts": verdicts(V), "caveats": caveats(V)}
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
