"""Headless assertions for the P10 demo (run by smoke.sh; also usable alone from the project folder):

    PYTHONPATH=. python demo/smoke_test.py            # engine-level checks (about 1 minute on CPU)

Every live number the demo shows is recomputed through engine.py (committed code paths) and compared with the
committed eval/results/text_minilm_v2.json within 1e-9. Exit code 1 on any failure.
"""
from __future__ import annotations

import hashlib
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine import BUNDLE, Engine  # noqa: E402

from components.attack.inject import inject_seq, oracle_grid  # noqa: E402
from components.robust_conformal.certify import features_from_docs  # noqa: E402

TOL = 1e-9
results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = ""):
    results.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}", flush=True)


def close(name: str, live: float, ref: float, tol: float = TOL):
    check(name, abs(live - ref) <= tol, f"live={live:.12g} committed={ref:.12g}")


def main() -> int:
    t0 = time.time()
    e = Engine()
    check("engine init", True, f"{time.time() - t0:.1f} s")
    c = e.committed
    fus = c["ablation"]["fusion"]

    # bundle integrity
    size = sum(p.stat().st_size for p in BUNDLE.iterdir() if p.is_file())
    check("bundle < 20 MB", size < 20e6, f"{size / 1e6:.2f} MB")
    bad = [n for n, m in e.manifest["files"].items() if hashlib.sha256((BUNDLE / n).read_bytes()).hexdigest() != m["sha256"]]
    check("bundle hashes match manifest", not bad, ",".join(bad))

    # conformal anchors
    close("CQR offset Q", e.Q, fus["cqr_offset_Q"])
    close("live ACI coverage (fusion cqr_aci)", e.aci_clean["coverage"], fus["cqr_aci"]["coverage"])
    close("live ACI mean daily coverage", e.aci_clean["mean_day_coverage"], fus["cqr_aci"]["mean_day_coverage"])
    close("clean symmetric CQR coverage", float(e.base_cov.mean()), c["attack"]["oracle"]["clean_cqr_coverage"])
    for k in (1, 2, 3, 5):
        lo, hi = e.cc(k).intervals(e.X, e.test_docs)
        close(f"certified clean k={k} coverage", float(np.mean((e.y >= lo) & (e.y <= hi))), c["spike"][f"clean_k{k}"]["coverage"])
        close(f"certified clean k={k} mean width", float(np.mean(hi - lo)), c["spike"][f"clean_k{k}"]["mean_width"])

    # pump replay (committed sentiment and trust), k = 3
    pump = c["attack"]["pump"]
    close("trust_of(fresh account) = committed pump trust", e.trust(0, 1.0, False, 1), pump["pump_trust"])
    P = e.population([pump["pump_sentiment"]] * 3, [pump["pump_trust"]] * 3, 3)
    close("pump: plain CQR coverage", P["plain_coverage"], pump["vanilla_cqr"]["coverage"])
    close("pump: certified coverage", P["certified_coverage"], pump["certified"]["coverage"])
    close("pump: median shift mean", P["median_shift_mean"], pump["median_shift_mean"])
    close("pump: median shift p95 |.|", P["median_shift_p95_abs"], pump["median_shift_p95_abs"])
    close("pump: plain ACI coverage", P["aci_plain"]["coverage"], c["spike"]["cr_aci"]["cqr_aci_pump"]["coverage"])
    close("pump: CR-ACI coverage", P["cr_aci"]["coverage"], c["spike"]["cr_aci"]["cr_aci_pump"]["coverage"])
    check("pump: certified contains clean interval on every row", P["certified_contains_clean_all_rows"])

    # worst fixed variant and beyond budget
    w0 = c["attack"]["oracle"]["all_variants"][0]
    W = e.population(w0["sents"], w0["trusts"], 3)
    close("worst fixed variant: plain coverage", W["plain_coverage"], c["attack"]["oracle"]["worst3"][0]["vanilla_coverage"])
    close("worst fixed variant: certified coverage", W["certified_coverage"], c["attack"]["oracle"]["worst3"][0]["certified_coverage"])
    for b in c["attack"]["beyond_budget"]:
        j = b["injected"]
        B = e.population(list(np.resize(w0["sents"], j)), list(np.resize(w0["trusts"], j)), 3)
        close(f"beyond budget {j} posts: plain coverage", B["plain_coverage"], b["vanilla_coverage"])
        close(f"beyond budget {j} posts: certified k=3 coverage", B["certified_coverage"], b["certified_k3_coverage"])

    # full 53-variant oracle and the showcase's flippable count
    ti = e.ti
    ok = np.ones(len(e.y), bool)
    for sv, tv in oracle_grid(3):
        Xv = e.X.copy()
        Xv[:, ti] = np.stack([features_from_docs(*inject_seq(a, b, sv, tv)) for a, b in e.test_docs])
        a0, a2 = e.fm.models[0].predict(Xv), e.fm.models[2].predict(Xv)
        ok &= (e.y >= np.minimum(a0, a2) - e.Q) & (e.y <= np.maximum(a0, a2) + e.Q)
    close("oracle (53 variants) plain CQR coverage", float(ok.mean()), c["attack"]["oracle"]["vanilla_cqr_oracle_coverage"])
    check("showcase flippable count reproduces", int((e.base_cov & ~ok).sum()) == e.showcase["n_flippable"],
          f"{int((e.base_cov & ~ok).sum())} vs {e.showcase['n_flippable']}")

    # random within-budget attacks: certified containment never fails
    rows = [e.row_of(d["ticker"], d["date"]) for d in e.showcase["days"]]
    rows += [e.random_row(s) for s in range(20)]
    viol, broken, n_att = 0, 0, 0
    for r in rows:
        for k in (1, 3, 5):
            rt = e.redteam(r, k, n=2000 if k == 3 else 500, seed=r + k, beyond=False)
            viol += rt["within"]["cert_containment_violations"] + rt["within"]["cert_missed_y_when_clean_covered"]
            broken += rt["within"]["plain_broken"]
            n_att += rt["within"]["n"]
    check("random within-budget attacks: 0 certified containment violations", viol == 0,
          f"{n_att:,} attacks on {len(rows)} days at k=1/3/5; plain CQR broken {broken:,} times")

    # per-day attack on every showcase day breaks plain with its cheapest grid variant, certified holds
    allheld = True
    for r in rows[:6]:
        f = e.flips(r, 3)
        allheld &= f["n_flipping"] > 0 and f["n_flipping_cert_survives"] == f["n_flipping"]
    check("every showcase day: some grid attack flips plain, certified survives all", allheld)

    n_fail = sum(not ok_ for _, ok_, _ in results)
    print(f"\nsmoke_test: {len(results) - n_fail}/{len(results)} passed in {time.time() - t0:.1f} s")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
