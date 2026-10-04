"""Headless checks for the Ghost Market demo (called by demo/smoke.sh; exits non-zero on any failure).

1. Data loads: demo/data/*.js parse as JSON, total under 5 MB; the page loads only local files.
2. Key numbers: the claims snapshot in the data equals eval/results/claims.json, and every claims key the page
   references exists there.
3. Integrity: exported treatment-minus-ghost gaps at T1 (1,200 s after 09:35) equal the committed
   E7_size_q*.csv (synced, five sizes), E4_nsr_naive.csv (naive, 4,000) and E8_ablation_val.csv (IA_sched_only)
   rows for the exported seeds; IS terms match too; every twin pair is identical before 09:35.
4. Recomputed statistics: the per-size means and the registered slope equal realism_scorecard.json and
   claims.json; the cross-seed gap stds equal nsr_E4_*.json; the own-impact stds give claims' 6x; the cold open's
   E10 arm means equal E10_replication_test.csv and their difference equals claims e10_dis.
5. Wording: phrases retired by the 4 Oct demo review are absent; their replacements are present.
"""
from __future__ import annotations

import csv
import glob
import json
import math
import os
import re
import sys

DEMO = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(DEMO)
RES = os.path.join(ROOT, "eval", "results")
FAIL = []


def check(ok, msg):
    print(("  ok   " if ok else "  FAIL ") + msg)
    if not ok:
        FAIL.append(msg)


def load_js(path):
    s = open(path).read()
    body = s[s.index("= ", s.rindex("window.")) + 2:].rstrip().rstrip(";")
    return json.loads(body)


def rows(f, label):
    return {int(r["seed"]): r for r in csv.DictReader(open(os.path.join(RES, f))) if r["label"] == label}


def std(v):
    m = sum(v) / len(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))


def close(a, b, rel=2e-5, abs_=1e-9):
    return abs(a - b) <= max(abs_, rel * max(abs(a), abs(b)))


def main():
    print("1. data loads")
    files = sorted(glob.glob(os.path.join(DEMO, "data", "*.js")))
    total = sum(os.path.getsize(f) for f in files)
    P = load_js(os.path.join(DEMO, "data", "summary.js"))
    shows = {int(re.search(r"showcase_(\d+)", f).group(1)): load_js(f) for f in files if "showcase_" in f}
    check(len(files) >= 2 and total < 5e6, f"{len(files)} data files, {total / 1e6:.2f} MB (< 5 MB)")
    html = open(os.path.join(DEMO, "index.html")).read()
    srcs = re.findall(r'<script src="([^"]+)"', html)
    check(all(os.path.exists(os.path.join(DEMO, s)) for s in srcs), f"page scripts exist locally: {srcs}")
    check(not re.search(r'(src|href)="https?://', html), "no CDN or remote assets in index.html")
    check("SIMULATED (ABIDES" in html and html.count("SIMULATED (ABIDES") >= 2, "SIMULATED (ABIDES) label in the header and on every chart")
    for s, sh in shows.items():
        w = sh["worlds"]
        check(len(w["ghost"]["mid2"]) == 2101 and all(len(w[k]["lad"]) == 1051 for k in w),
              f"showcase {s}: {len(w)} worlds, 1 s mids and 2 s top-5 ladders 09:30-10:05")

    print("2. key numbers equal eval/results/claims.json")
    claims = json.load(open(os.path.join(RES, "claims.json")))
    check(P["claims"] == claims, "data/summary.js claims snapshot == claims.json (all keys)")
    used = set(re.findall(r'data-c="(\w+)"', html)) | set(re.findall(r'\b(?:c|num)\("(\w+)"\)', html))
    for k in re.findall(r'k: \["(\w+)", "(\w+)", "(\w+)"\]', html):
        used |= set(k)
    used |= set(re.findall(r', n: "(\w+)"', html))
    for k in re.findall(r'\["[^"]+", "(fb_\w+)"\]', html):
        used |= {k, k + "_lo", k + "_hi"}
    missing = sorted(k for k in used if k not in claims)
    check(not missing and len(used) > 40, f"{len(used)} claims keys referenced by the page, missing: {missing}")
    check(P["scorecard"] == json.load(open(os.path.join(RES, "realism_scorecard.json"))), "scorecard snapshot == realism_scorecard.json")
    nsr = json.load(open(os.path.join(RES, "nsr_E4_nsr_naive_vs_E4_nsr_sync.json")))
    check(P["nsr"] == nsr, "nsr snapshot == nsr_E4_nsr_naive_vs_E4_nsr_sync.json")
    e1 = json.load(open(os.path.join(RES, "nsr_E1_calib_train.json")))
    check(P["nsr_e1"] == e1, "nsr_e1 snapshot == nsr_E1_calib_train.json")
    x = e1["exps"]["E1_calib_train"]
    check(f"{x['60']['std']:.1f}" == claims["gap_std_60"] and f"{x['1200']['std']:.0f}" == claims["gap_std_1200"]
          and f"{x['300']['mean']:.1f}" == claims["gap_mean_300"],
          f"E1 horizons: std {x['60']['std']:.2f} (1 min) / {x['1200']['std']:.2f} (20 min), mean {x['300']['mean']:.2f} (5 min) "
          f"== claims; same-horizon means shown: {x['60']['mean']:+.1f} / {x['1200']['mean']:+.1f}")
    sc0 = P["scorecard"]
    check(f"{100 * sc0['boot_valid_frac']:.0f}" == claims["e7_valid_pct"], f"usable bootstrap draws {100 * sc0['boot_valid_frac']:.0f}% == claims e7_valid_pct")

    print("3. integrity: exported T1 gaps == committed CSVs")
    seeds, A = P["meta"]["seeds"], P["arms"]
    j1 = P["meta"]["t1_s"] // P["meta"]["grid_s"]
    for arm, f, label in [(f"sync_{q}", f"E7_size_q{q}.csv", "TWAP") for q in P["meta"]["sizes"]] + \
                         [("naive_4000", "E4_nsr_naive.csv", "TWAP"), ("ia_4000", "E8_ablation_val.csv", "IA_sched_only"),
                          ("sync_4000", "E8_ablation_val.csv", "TWAP")]:
        R = rows(f, label)
        bad = [s for i, s in enumerate(seeds) if A[arm]["t1"][i] != float(R[s]["impact_end_cents"])]
        check(not bad, f"{arm:10s} vs {f} [{label}]: {len(seeds)} seeds, T1 gap equal (impact_end_cents){' BAD ' + str(bad) if bad else ''}")
        terms = [("is_bps", "is_bps"), ("own_bps", "own_impact_bps"), ("drift_bps", "drift_bps"), ("instant_bps", "instant_bps")]
        bad = [(s, k) for i, s in enumerate(seeds) for k, col in terms if not close(A[arm][k][i], float(R[s][col]))]
        check(not bad, f"{arm:10s} vs {f} [{label}]: IS, own impact, drift, instant equal to CSV precision{' BAD ' + str(bad[:3]) if bad else ''}")
        check(all(r["pre_window_identical"] == "True" for r in R.values() if r is not None), f"{f} [{label}]: committed pre_window_identical True")
        check(all(A[arm]["gap2"][i][j1] == round(2 * A[arm]["t1"][i]) for i in range(len(seeds))), f"{arm:10s}: path at T1 == exported T1")
        check(all(A[arm]["ident_ok"]) and all(A[arm]["top1_exact"]),
              f"{arm:10s}: pre-trade top-5 book events identical on every seed (min n = {min(n for _, n in A[arm]['ident'])}), tca.pre_window_exact True")

    print("4. recomputed statistics == committed results")
    sc = P["scorecard"]
    means = [sum(A[f"sync_{q}"]["t1"]) / len(seeds) for q in P["meta"]["sizes"]]
    check(all(close(m, r, 1e-12) for m, r in zip(means, sc["peak_mean_cents"])), f"per-size mean T1 gap {[round(m, 3) for m in means]} == scorecard peak_mean_cents")
    lp = [math.log(x) for x in sc["participation"]]
    lm = [math.log(x) for x in means]
    mx, my = sum(lp) / len(lp), sum(lm) / len(lm)
    slope = sum((a - mx) * (b - my) for a, b in zip(lp, lm)) / sum((a - mx) ** 2 for a in lp)
    check(close(slope, sc["delta"], 1e-9) and f"{slope:.2f}" == claims["e7_delta"], f"registered slope recomputed {slope:.4f} == claims e7_delta {claims['e7_delta']}")
    for arm, e in [("naive_4000", "E4_nsr_naive"), ("sync_4000", "E4_nsr_sync")]:
        for h, ref in nsr["exps"][e].items():
            v = [p[int(h) // P["meta"]["grid_s"]] / 2 for p in A[arm]["gap2"]]
            check(close(std(v), ref["std"], 1e-9) and close(sum(v) / len(v), ref["mean"], 1e-9, 1e-9),
                  f"{e} @ {h:>4s}s: std {std(v):6.2f} mean {sum(v) / len(v):+6.2f} == nsr json")
    a, b = std(A["naive_4000"]["own_bps"]), std(A["sync_4000"]["own_bps"])
    check(f"{a:.2f}" == claims["own_std_naive"] and f"{b:.2f}" == claims["own_std_sync"] and f"{a / b:.0f}" == claims["noise_reduction"],
          f"own-impact std naive {a:.2f} / synced {b:.2f} = {a / b:.1f}x == claims {claims['own_std_naive']} / {claims['own_std_sync']} / {claims['noise_reduction']}x")
    for s, sh in shows.items():
        i = seeds.index(s)
        st = sh["worlds"]["twap_4000"]["stats"]
        check(st["t1"] == A["sync_4000"]["t1"][i] and sh["worlds"]["ia_4000"]["stats"]["t1"] == A["ia_4000"]["t1"][i],
              f"showcase {s}: stats agree with summary")
        g, w = sh["worlds"]["ghost"]["mid2"], sh["worlds"]["twap_4000"]["mid2"]
        check(g[300 + 1200] - w[300 + 1200] == round(2 * st["t1"]), f"showcase {s}: ghost mid − our mid at 09:55 == T1 gap")
    r10 = list(csv.DictReader(open(os.path.join(RES, "E10_replication_test.csv"))))
    tw = {r["seed"]: float(r["is_bps"]) for r in r10 if r["label"] == "TWAP"}
    ia = {r["seed"]: float(r["is_bps"]) for r in r10 if r["label"] == "IA_sched_only"}
    E = P["e10"]
    mt, mi = sum(tw.values()) / len(tw), sum(ia.values()) / len(ia)
    check(E["n"] == len(tw) == int(claims["e10_n"]) and close(E["twap_is_mean"], mt, 1e-12) and close(E["ia_is_mean"], mi, 1e-12)
          and f"{mi - mt:+.3f}" == claims["e10_dis"],
          f"cold open: E10 means TWAP {mt:.4f} / agent {mi:.4f} bps (n = {len(tw)}) == CSV; difference {mi - mt:+.4f} == claims e10_dis {claims['e10_dis']}")

    print("5. wording (4 Oct demo review)")
    texts = {f: open(os.path.join(DEMO, f)).read() for f in ("index.html", "SCRIPT.md", "README.md")}
    retired = ["0.03 bp", "does not replicate", "single-seed differences are noise", "1 seed: noise", "single seeds are noisy",
               "single-seed noise", "tighter paired confidence intervals", "tighter paired CI", "re-key every agent",
               "shifts every later random draw", "spread and book-walking", "Type any seed", "Why sub-tick claims need the twin"]
    hits = [(f, p) for f, t in texts.items() for p in retired if p.lower() in t.lower()]
    check(not hits, f"{len(retired)} retired phrases absent from index.html, SCRIPT.md, README.md{' FOUND ' + str(hits) if hits else ''}")
    need = ["one seed cannot establish an average advantage", "of bootstrap draws usable", "re-key every background agent",
            "can desynchronise state-dependent random draws", "smaller paired-difference std", "median of 4 policies",
            "decision-to-fill", "E10 did not confirm superiority", "The twin coupling made", "the ghost attributes it",
            "0–2,147,483,647", "Here's why you can trust that answer", "1 new seed (live, synced)", "live paused (memory guard)",
            "E10 aggregate, fixed at 4,000 shares", "id=\"a1qty\"", "id=\"a1agg\""]
    miss = [p for p in need if p.lower() not in texts["index.html"].lower()]
    check(not miss, f"{len(need)} required phrases present in index.html{' MISSING ' + str(miss) if miss else ''}")
    shots = sorted(os.listdir(os.path.join(DEMO, "fallback")))
    check(len(shots) >= 8 and all(f.endswith(".png") for f in shots), f"fallback/: {len(shots)} screenshots")

    print(f"\n{'ALL CHECKS PASSED' if not FAIL else str(len(FAIL)) + ' CHECK(S) FAILED'}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
