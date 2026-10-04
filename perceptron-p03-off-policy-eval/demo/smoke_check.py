"""Headless smoke test for the P3 demo (run by demo/smoke.sh). Offline; needs only the committed files and numpy.

Checks, each PASS/FAIL (exit 0 only if all pass):
  1. extract: sha256 matches demo/data/extract_manifest.json; every committed demo file < 20 MB; manifest checks passed
  2. extract -> committed numbers, recomputed here with the standard library (independent of knob.py):
     CTRs 4.890 / 3.442 per 1,000, halves naive +1.62 and reference +1.26, IPW halves-deploy effect (obd_slice.json)
  3. knob: demo/knob.py re-run from the extract reproduces demo/results/knob_results.json and knob_summary.md byte for byte
  4. knob results: 12 series x 101 alphas; reproduction 58/58; closed forms vs gate.py 12/12; P1/P2 all hold;
     gate flips (first can't-tell alpha per series, scanning away from the logging policy) reported
  5. page: demo/build.py rebuild is byte-identical to the committed demo/index.html; the inlined headline numbers equal
     the committed JSON; the knob grid is inlined; no external resources; inline JS parses (node --check, if node exists)
  6. run.sh: P3_NO_OPEN=1 demo/run.sh finishes, and the time to the page is < 60 s
  7. fallback screenshots: demo/fallback/ holds PNGs, total < 5 MB
"""
from __future__ import annotations

import gzip
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

DEMO = Path(__file__).resolve().parent
ROOT = DEMO.parent
RES = ROOT / "eval" / "results"
PY = sys.executable
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""), flush=True)


def close(a, b, rel):
    return abs(a - b) <= rel * max(abs(a), abs(b), 1e-300)


def main():
    man = json.loads((DEMO / "data" / "extract_manifest.json").read_text())
    pre = json.loads((RES / "obd_slice.json").read_text())

    # 1. extract integrity and sizes
    shas = {n: hashlib.sha256((DEMO / "data" / n).read_bytes()).hexdigest() for n in man["files"]}
    check("extract sha256 matches the manifest", all(shas[n] == m["sha256"] for n, m in man["files"].items()))
    big = [(str(p.relative_to(ROOT)), p.stat().st_size) for p in DEMO.rglob("*") if p.is_file() and p.stat().st_size >= 20_000_000]
    ext_mb = sum((DEMO / "data" / n).stat().st_size for n in man["files"]) / 1e6
    check("every demo file < 20 MB (PLAYBOOK §6)", not big, f"extract {ext_mb:.2f} MB" + (f"; too big: {big}" if big else ""))
    check("extract manifest: raw-vs-extract and committed-number checks passed at vendoring", man["all_checks_pass"] is True)

    # 2. committed numbers straight from the extract (standard library)
    def rows(name):
        with gzip.open(DEMO / "data" / name, "rt") as f:
            next(f)
            return [ln.rstrip("\n").split(",") for ln in f]
    B, R = rows("obd_bts_all.csv.gz"), rows("obd_random_all.csv.gz")
    def ctr(rs, hours, rnd):
        n = c = 0
        for x in rs:
            if int(x[0]) in hours and not (rnd and x[4] == "1"):
                n += int(x[5]); c += int(x[5]) * int(x[3] if rnd else x[4])
        return c / n
    W, H1, H2 = set(range(84)), set(range(42)), set(range(42, 84))
    A = pre["a3_halves"]["A_deploy_BTS"]
    b2, r1, r2 = ctr(B, H2, False), ctr(R, H1, True), ctr(R, H2, True)
    ipw = math.fsum(int(x[5]) * (1.0 / 80) / float(x[3]) for x in B if int(x[0]) in H2 and x[4] == "1") / sum(int(x[5]) for x in B if int(x[0]) in H2)
    for label, ours, ref in (("BTS CTR in W (4.890 per 1,000)", ctr(B, W, False), pre["a2"]["truth"]),
                             ("Random CTR in W (3.442 per 1,000)", ctr(R, W, True), pre["a2"]["random_ctr"]),
                             ("halves naive before/after (+1.62)", b2 - r1, A["naive"]),
                             ("halves concurrent A/B reference (+1.26)", b2 - r2, A["truth"]),
                             ("halves IPW deploy effect (+1.39)", b2 - ipw, A["IPW"]["policy_effect_after"])):
        check(f"extract reproduces {label}", close(ours, ref, 1e-12), f"{1000 * ours:.6f} vs committed {1000 * ref:.6f} per 1,000")

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        # 3. knob recompute
        t = time.time()
        p = subprocess.run([PY, str(DEMO / "knob.py"), "--out", str(td / "knob")], capture_output=True, text=True)
        same = p.returncode == 0 and all((td / "knob" / f).read_bytes() == (DEMO / "results" / f).read_bytes() for f in ("knob_results.json", "knob_summary.md"))
        check("knob.py re-run from the extract reproduces the committed results byte for byte", same,
              f"{time.time() - t:.1f} s" + ("" if p.returncode == 0 else f"; knob.py failed: {p.stderr[-400:]}"))
        # 4. knob results content
        kr = json.loads((DEMO / "results" / "knob_results.json").read_text())
        shape = len(kr["series"]) == 12 and all(len(s["rows"]) == 101 for s in kr["series"].values()) and len(kr["grid"]) == 101
        check("knob grid: 12 series × 101 α", shape)
        check("knob reproduction checks vs committed far-end cells", all(c["ok"] for c in kr["reproduction"]), f"{sum(c['ok'] for c in kr['reproduction'])}/{len(kr['reproduction'])}")
        check("knob closed forms vs gate.py on per-row arrays", all(kr["crosscheck"].values()), f"{sum(kr['crosscheck'].values())}/{len(kr['crosscheck'])} series")
        check("knob P1/P2 (logging end exact; algebra)", all(all(v2 for v2 in v.values() if isinstance(v2, bool)) for v in kr["p1_p2"].values()))
        flips = {k: s["summary"]["first_abstain"] for k, s in kr["series"].items()}
        interior = {k: a for k, a in flips.items() if a is not None and a > 0.015}
        check("gate flips from answer to can't-tell inside (0, 1) for at least one series", bool(interior),
              "first can't-tell α: " + ", ".join(f"{k} {'never' if a is None else f'{a:.2f}'}" for k, a in flips.items()))
        # 5. page rebuild and contents
        p = subprocess.run([PY, str(DEMO / "build.py"), "--out", str(td / "index.html")], capture_output=True, text=True)
        check("build.py runs and asserts its numbers against eval/results/headline.json", p.returncode == 0, (p.stdout.strip().split("; ")[-1] if p.returncode == 0 else p.stderr[-400:]))
        check("rebuilt page is byte-identical to the committed demo/index.html", p.returncode == 0 and (td / "index.html").read_bytes() == (DEMO / "index.html").read_bytes())
        html = (DEMO / "index.html").read_text()
        data = json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S).group(1).replace("<\\/", "</"))
        ks = data["knob"]["series"]
        check("page inlines the knob grid", len(ks) == 12 and all(len(s["f"]["IPW"]["v"]) == 101 and len(s["f"]["bits"]) == 101 for s in ks.values()))
        w2 = ks["W2·SB"]["f"]["IPW"]["v"][100] / 1000
        check("page knob endpoint W2 · BTS logs · α=1 equals the committed halves IPW cell",
              close(w2, pre["a3_halves"]["cells"]["B2"]["v"] - A["IPW"]["policy_effect_after"], 1e-5), f"{1000 * w2:.4f} per 1,000")
        def span(src_part):
            m = re.search(r'data-src="[^"]*' + re.escape(src_part) + r'[^"]*"[^>]*>([^<]+)<', html)
            return m.group(1) if m else None
        hl = json.loads((RES / "headline.json").read_text())["display"]
        pairs = [("a3_halves.A_deploy_BTS.naive ×1000", hl["a3A_naive_k"]), ("a3_halves.A_deploy_BTS.truth ×1000 (concurrent", hl["a3A_truth_k"]),
                 ("a3_halves.A_deploy_BTS.DR.policy_effect_after ×1000", hl["a3A_dr_k"]), ("a2.P-hourly.DR.value ×1000", hl["a2_hourly_dr_k3"]),
                 ("a2.truth ×1000 (BTS arm", hl["obd_ctr_bts_k3"]), ("halves_A.block_lo", hl["bb_A_lo"]), ("halves_A.block_hi", hl["bb_A_hi"])]
        got = [(want, span(src)) for src, want in pairs]
        check("headline numbers on the page equal eval/results/headline.json", all(g == w for w, g in got), " · ".join(f"{g}" for _, g in got))
        ext = re.findall(r"""(?:src|href)\s*=\s*["'](?:https?:)?//|url\(\s*["']?https?:|@import|<link[^>]+stylesheet""", html)
        check("page loads no external resources (no CDN, no web fonts)", not ext, f"{len(html.encode()) / 1e3:.0f} kB single file")
        if shutil.which("node"):
            js = re.findall(r"<script>(.*?)</script>", html, re.S)[-1]
            (td / "page.js").write_text(js)
            p = subprocess.run(["node", "--check", str(td / "page.js")], capture_output=True, text=True)
            check("inline JS parses (node --check)", p.returncode == 0, p.stderr[-300:])
        else:
            print("[SKIP] node not found: JS syntax check skipped")
    # 6. run.sh timing
    t = time.time()
    p = subprocess.run(["bash", str(DEMO / "run.sh")], env={**os.environ, "P3_NO_OPEN": "1", "P3_PYTHON": PY}, capture_output=True, text=True)
    dt = time.time() - t
    check("run.sh (P3_NO_OPEN=1) finishes and the page is ready in < 60 s", p.returncode == 0 and dt < 60, f"{dt:.1f} s" + ("" if p.returncode == 0 else f"; {p.stdout[-300:]}{p.stderr[-300:]}"))
    # 7. fallback
    pngs = list((DEMO / "fallback").glob("*.png"))
    tot = sum(x.stat().st_size for x in DEMO.joinpath("fallback").rglob("*") if x.is_file())
    check("fallback screenshots present, total < 5 MB", pngs and tot < 5_000_000, f"{len(pngs)} PNG, {tot / 1e6:.2f} MB")

    n_fail = sum(not ok for _, ok, _ in results)
    print(f"\nsmoke: {len(results) - n_fail}/{len(results)} checks passed" + (" — FAIL" if n_fail else " — PASS"))
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
