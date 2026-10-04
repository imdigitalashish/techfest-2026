"""Pre-registered alpha-knob analysis on REAL data (the Open Bandit Dataset extract in demo/data/).

Implements demo/preregistration_knob.md (commit 10209ca, registered 2026-10-04 21:07:33 IST, before any knob computation).
Reproduce (from perceptron-p03-off-policy-eval/; numpy required):
  python3 demo/knob.py                  # writes demo/results/knob_results.json and demo/results/knob_summary.md
  python3 demo/knob.py --out /tmp/k     # same, elsewhere (used by demo/smoke.sh)

Candidate pi_a = (1 - a) BTS + a uniform. Series = period x log source. lam = far-end share (BTS logs: a; Random logs: 1 - a);
weights w = (1 - lam) + lam x with x the far-end weight (BTS logs: (1/80)/ps, exact; Random logs: pi_hourly/0.0125).
All statistics are exact functions of per-hour sufficient statistics summed with math.fsum (deterministic on any machine).
Gate decisions: components/report/gate.py decide() with the frozen eval/gate_rule.json; the diagnostics are cross-checked
against gate.py diagnostics() on the expanded per-row arrays at 11 values of alpha per series.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from components.report.gate import decide, diagnostics, load_rule  # noqa: E402  (frozen rule, b4e95ae)

DATA = ROOT / "demo" / "data"
RES = ROOT / "eval" / "results"
Z = 1.959963984540054
GRID = [i / 100 for i in range(101)]
CHECK_ALPHAS = [i / 10 for i in range(11)]
PREREG = {"file": "demo/preregistration_knob.md", "commit": "10209ca915cb47659d167617b771414fec3c1ecc",
          "registered_at": "2026-10-04 21:07:33 IST"}
PERIODS = [  # id, label, first hour, last hour + 1, include the 3 Random rows logged before the first BTS row
    ("W", "W · all 84 h (pre-registered window)", 0, 84, False),
    ("W1", "W1 · first half (pre-registered)", 0, 42, False),
    ("W2", "W2 · second half (pre-registered)", 42, 84, False),
    ("D24", "Nov 24 · whole UTC day", 0, 24, True),
    ("D25", "Nov 25 · whole UTC day", 24, 48, True),
    ("D26", "Nov 26 · whole UTC day", 48, 72, True),
]
SOURCES = {"SB": "BTS logs · exact weights from logged propensities (primary)",
           "SR": "Random logs · P-hourly reconstruction of BTS (approximate target)"}
EST = ("IPW", "SNIPW")
# Pre-registered predictions (demo/preregistration_knob.md §11), keyed by (period, source).
PRED = {
    ("W2", "SB"): dict(gate=0.43, e1=None, e2="holds"),
    ("D26", "SB"): dict(gate=0.40, e1=0.28, e2="fails"),
    ("D25", "SB"): dict(gate="all", e1=0.43, e2="holds"),
    ("W1", "SB"): dict(gate="all", e1=None, e2="holds"),
    ("D24", "SB"): dict(gate=0.12, cond="abs(z) <= 3", e1=None, e2="holds"),
    ("W", "SB"): None,
    **{(p, "SR"): dict(gate=None, e1=None, e2="holds") for p in ("W", "W2", "D26", "D25")},
    ("W1", "SR"): dict(gate=None, cond="abs(z) <= 3", e1=None, e2="holds"),
    ("D24", "SR"): dict(gate=None, cond="abs(z) <= 3", e1=None, e2="holds"),
}


def fs(a) -> float:
    return math.fsum(np.asarray(a, dtype=float).tolist())


def read_extract():
    man = json.loads((DATA / "extract_manifest.json").read_text())
    for name, meta in man["files"].items():
        got = hashlib.sha256((DATA / name).read_bytes()).hexdigest()
        if got != meta["sha256"]:
            sys.exit(f"{name}: sha256 {got} does not match the manifest — refusing to run (pre-registration §2)")

    def rows(name, header):
        with gzip.open(DATA / name, "rt", newline="") as f:
            rd = csv.reader(f)
            assert next(rd) == header, name
            return list(rd)

    b = rows("obd_bts_all.csv.gz", ["hour", "item", "position", "propensity", "click", "count"])
    r = rows("obd_random_all.csv.gz", ["hour", "item", "position", "click", "pre_t0", "count"])
    B = {k: np.array([int(x[i]) for x in b]) for k, i in (("h", 0), ("item", 1), ("pos", 2), ("click", 4), ("k", 5))}
    B["ps"] = np.array([float(x[3]) for x in b])
    R = {k: np.array([int(x[i]) for x in r]) for k, i in (("h", 0), ("item", 1), ("pos", 2), ("click", 3), ("pre", 4), ("k", 5))}
    R["ps"] = np.full(len(r), 0.0125)
    return man, B, R


def p_hourly(B):
    """The committed P-hourly reconstruction (eval/run_obd_slice.py): hourly empirical item shares per position over W."""
    cnt = np.zeros((84, 80, 3))
    np.add.at(cnt, (B["h"], B["item"], B["pos"] - 1), B["k"].astype(float))
    tot = cnt.sum(1, keepdims=True)
    return np.divide(cnt, tot, out=np.zeros_like(cnt), where=tot > 0)


def arm_stats(d, x, hours):
    """Sufficient statistics of one arm's tuples (x = far-end weight; None for the reference-only arm)."""
    k, r = d["k"].astype(float), d["click"].astype(float)
    out = {"n": fs(k), "Sr": fs(k * r), "hours": {}}
    if x is not None:
        out.update(Sx=fs(k * x), Sxx=fs(k * x * x), Sxr=fs(k * x * r), Sxxr=fs(k * x * x * r), max_x=float(x.max()))
    for h in hours:
        m = d["h"] == h
        hs = {"n": fs(k[m]), "Sr": fs(k[m] * r[m])}
        if x is not None:
            hs.update(Sx=fs(k[m] * x[m]), Sxr=fs(k[m] * x[m] * r[m]))
        out["hours"][h] = hs
    return out


def build_series(B, R, pi_h):
    out = {}
    for pid, label, h0, h1, incl_pre in PERIODS:
        hours = list(range(h0, h1))
        mB = (B["h"] >= h0) & (B["h"] < h1)
        mR = (R["h"] >= h0) & (R["h"] < h1) & ((R["pre"] == 0) | incl_pre)
        Bp = {k: v[mB] for k, v in B.items()}
        Rp = {k: v[mR] for k, v in R.items()}
        xB = (1.0 / 80) / Bp["ps"]
        xR = pi_h[Rp["h"], Rp["item"], Rp["pos"] - 1] / Rp["ps"]
        for src, (L, xL, O) in (("SB", (Bp, xB, Rp)), ("SR", (Rp, xR, Bp))):
            out[(pid, src)] = dict(period=pid, label=label, source=src, hours=hours, log=arm_stats(L, xL, hours),
                                   other=arm_stats(O, None, hours), _rows=(L, xL))
    return out


def cell(s, a, rule):
    """Every pre-registered quantity at one alpha for one series (closed forms; see the module docstring)."""
    L, O, src, hours = s["log"], s["other"], s["source"], s["hours"]
    lam = a if src == "SB" else 1.0 - a
    c, d = (1.0 - a, a) if src == "SB" else (a, 1.0 - a)  # weights of the logging arm's / other arm's CTR in the reference
    n, no = L["n"], O["n"]
    pbar, qbar = L["Sr"] / n, O["Sr"] / no
    se_p, se_q = math.sqrt(pbar * (1 - pbar) / (n - 1)), math.sqrt(qbar * (1 - qbar) / (no - 1))
    ref = (1.0 - a) * (pbar if src == "SB" else qbar) + a * (qbar if src == "SB" else pbar)
    se_ref = math.sqrt(c * c * se_p * se_p + d * d * se_q * se_q)
    Sw = n * (1 - lam) + lam * L["Sx"]
    Sww = n * (1 - lam) ** 2 + 2 * lam * (1 - lam) * L["Sx"] + lam * lam * L["Sxx"]
    Swr = (1 - lam) * L["Sr"] + lam * L["Sxr"]
    Swwr = (1 - lam) ** 2 * L["Sr"] + 2 * lam * (1 - lam) * L["Sxr"] + lam * lam * L["Sxxr"]
    wbar = Sw / n
    var_x = max((L["Sxx"] - L["Sx"] ** 2 / n) / (n - 1), 0.0)
    sd_w = lam * math.sqrt(var_x)
    z = (lam * (L["Sx"] / n - 1.0)) / (sd_w / math.sqrt(n)) if sd_w > 0 else (0.0 if math.isclose(wbar, 1.0, rel_tol=1e-5, abs_tol=1e-8) else math.inf)
    diag = {"ess_frac": Sw * Sw / (n * Sww), "ess_r": Swr * Swr / Swwr if Swwr > 0 else 0.0, "z_mean_w": z}
    answer, why = decide(diag, rule)
    H = len(hours)
    hc = H / (H - 1)
    ref_h = [c * (L["hours"][h]["Sr"] - L["hours"][h]["n"] * pbar) / n + d * (O["hours"][h]["Sr"] - O["hours"][h]["n"] * qbar) / no for h in hours]
    se_ref_cl = math.sqrt(hc * math.fsum(v * v for v in ref_h))
    row = dict(a=a, lam=lam, n=n, ess_frac=diag["ess_frac"], ess=diag["ess_frac"] * n, ess_r=diag["ess_r"], z=z,
               max_w=(1 - lam) + lam * L["max_x"], answer=bool(answer), why=why, ref=ref, se_ref=se_ref, se_ref_cl=se_ref_cl)
    Srr = n * pbar * (1 - pbar)
    for e in EST:
        if e == "IPW":
            v = Swr / n
            SS = Swwr - n * v * v
            C = (1 - pbar) * Swr
            S_h = [(1 - lam) * L["hours"][h]["Sr"] + lam * L["hours"][h]["Sxr"] - L["hours"][h]["n"] * v for h in hours]
        else:
            v = Swr / Sw
            SS = ((1 - 2 * v) * Swwr + v * v * Sww) / (wbar * wbar)
            C = ((1 - pbar - v) * Swr + v * pbar * Sw) / wbar
            S_h = [((1 - lam) * L["hours"][h]["Sr"] + lam * L["hours"][h]["Sxr"]
                    - v * ((1 - lam) * L["hours"][h]["n"] + lam * L["hours"][h]["Sx"])) / wbar for h in hours]
        SS = max(SS, 0.0)
        se = math.sqrt(SS / (n - 1) / n)
        se_cl = math.sqrt(hc * math.fsum(x * x for x in S_h)) / n
        G = max(SS - 2 * c * C + c * c * Srr, 0.0)
        d_se = math.sqrt(G / (n - 1) / n + d * d * se_q * se_q)
        D_h = [(S_h[j] - c * (L["hours"][h]["Sr"] - L["hours"][h]["n"] * pbar)) / n
               - d * (O["hours"][h]["Sr"] - O["hours"][h]["n"] * qbar) / no for j, h in enumerate(hours)]
        d_se_cl = math.sqrt(hc * math.fsum(x * x for x in D_h))
        gap = abs(v - ref)
        row[e] = dict(v=v, se=se, se_cl=se_cl, d_se=d_se, d_se_cl=d_se_cl,
                      E1=gap <= Z * se, E1_cl=gap <= Z * se_cl, E2=gap <= Z * d_se, E2_cl=gap <= Z * d_se_cl,
                      miss=max(gap - Z * se, 0.0), miss_cl=max(gap - Z * se_cl, 0.0))
    return row


def scan(src):
    return GRID if src == "SB" else GRID[::-1]


def summarise(s):
    rows = {r["a"]: r for r in s["rows"]}
    order = scan(s["source"])
    out = {"first_abstain": next((a for a in order if not rows[a]["answer"]), None),
           "answered_alphas": sum(rows[a]["answer"] for a in order)}
    out["abstain_all_but_logging_end"] = all(not rows[a]["answer"] for a in order[1:])
    for e in EST:
        for iv, k1, k2 in (("row", "E1", "E2"), ("cluster", "E1_cl", "E2_cl")):
            res = {}
            for ep in (k1, k2):
                ok = [rows[a][e][ep] for a in order]
                ans = [rows[a]["answer"] for a in order]
                res[ep.split("_")[0]] = dict(
                    first_fail=next((a for a, o in zip(order, ok) if not o), None),
                    answered_hold=sum(an and o for an, o in zip(ans, ok)), answered_miss=sum(an and not o for an, o in zip(ans, ok)),
                    unnecessary_abstention=sum((not an) and o for an, o in zip(ans, ok)),
                    justified_abstention=sum((not an) and (not o) for an, o in zip(ans, ok)),
                    holds_all=all(ok), crossings=sum(ok[i] != ok[i + 1] for i in range(len(ok) - 1)))
            res["E1"]["max_answered_miss"] = max([rows[a][e]["miss" if iv == "row" else "miss_cl"] for a in order if rows[a]["answer"]] or [0.0])
            out[f"{e}_{iv}"] = res
    return out


def grade_predictions(series):
    out = {}
    for (pid, src), pred in PRED.items():
        s = series[(pid, src)]
        sm, key = s["summary"], f"{pid}·{src}"
        if pred is None:
            out[key] = {"predicted": "not predicted", "result": f"first abstain {sm['first_abstain']}", "grade": "n/a"}
            continue
        g = {}
        far = s["rows"][-1] if src == "SB" else s["rows"][0]
        cond_ok = abs(far["z"]) <= 3.0 if "cond" in pred else True
        if pred["gate"] == "all":
            g["gate"] = dict(predicted="abstain at every alpha except the logging end", result=sm["abstain_all_but_logging_end"],
                             grade="hit" if sm["abstain_all_but_logging_end"] else "miss")
        else:
            got = sm["first_abstain"]
            ok = (got is None and pred["gate"] is None) or (got is not None and pred["gate"] is not None and abs(got - pred["gate"]) < 1e-9)
            near = got is not None and pred["gate"] is not None and abs(got - pred["gate"]) <= 0.02 + 1e-9
            grade = "hit" if ok else ("near (±0.02)" if near else "miss")
            if not cond_ok:
                grade += f" (condition {pred['cond']} NOT met: far-end z {far['z']:+.2f})"
            g["gate"] = dict(predicted="never" if pred["gate"] is None else f"first abstain {pred['gate']:.2f}" + (f" if {pred['cond']}" if "cond" in pred else ""),
                             result="never" if got is None else f"first abstain {got:.2f}", grade=grade)
        e1 = sm["IPW_row"]["E1"]
        got = e1["first_fail"]
        if pred["e1"] is None:
            g["E1_IPW"] = dict(predicted="holds at every alpha", result="holds at every alpha" if got is None else f"fails from {got:.2f}",
                               grade="hit" if got is None else "miss")
        else:
            ok = got is not None and abs(got - pred["e1"]) < 1e-9
            near = got is not None and abs(got - pred["e1"]) <= 0.02 + 1e-9
            g["E1_IPW"] = dict(predicted=f"fails from {pred['e1']:.2f}", result="never fails" if got is None else f"fails from {got:.2f}",
                               grade="hit" if ok else ("near (±0.02)" if near else "miss"))
        e2 = sm["IPW_row"]["E2"]
        holds_away = e2["first_fail"] is None
        fails_away = all(not r["IPW"]["E2"] for r in (s["rows"][1:] if src == "SB" else s["rows"][:-1]))
        g["E2_IPW"] = dict(predicted=pred["e2"] + (" at every alpha" if pred["e2"] == "holds" else " at every alpha except the logging end"),
                           result="holds at every alpha" if holds_away else ("fails at every alpha except the logging end" if fails_away else f"mixed (first fail {e2['first_fail']})"),
                           grade="hit" if (pred["e2"] == "holds" and holds_away) or (pred["e2"] == "fails" and fails_away) else "miss")
        out[key] = g
    return out


def p1_p2(series):
    out = {}
    for (pid, src), s in series.items():
        rows = s["rows"]
        end, far = (rows[0], rows[-1]) if src == "SB" else (rows[-1], rows[0])
        ctr = s["log"]["Sr"] / s["log"]["n"]
        p1 = all(abs(end[e]["v"] - ctr) <= 1e-15 for e in EST) and abs(end["ess_frac"] - 1) <= 1e-12 and end["z"] == 0.0 and end["answer"] and all(end[e]["E1"] for e in EST)
        dfar = far["IPW"]["v"] - far["ref"]
        lin = max(abs((r["IPW"]["v"] - r["ref"]) - r["lam"] * dfar) for r in rows)
        zs = [abs(r["z"]) for r in rows if r["lam"] > 0]
        away = [r for r in rows if r["lam"] > 0]
        out[f"{pid}·{src}"] = dict(P1_logging_end_exact=bool(p1), P2_ipw_gap_linear_max_abs_dev=lin, P2_ipw_gap_linear=lin <= 1e-15,
                                   P2_abs_z_constant=(max(zs) - min(zs)) <= 1e-9 * max(zs + [1.0]),
                                   P2_E2_ipw_constant=len({r["IPW"]["E2"] for r in away}) == 1,
                                   P2_E1_ipw_single_crossing=s["summary"]["IPW_row"]["E1"]["crossings"] <= 1)
    return out


def reproduction(series):
    """Far-end cells vs committed results (pre-registration §10)."""
    pre = json.loads((RES / "obd_slice.json").read_text())
    dev = json.loads((RES / "obd_slice_deviation_floor.json").read_text())
    gp = {c["case"]: c for c in json.loads((RES / "gate_obd_posthoc.json").read_text())["cases"]}
    hA, hB, hc = pre["a3_halves"]["A_deploy_BTS"], pre["a3_halves"]["B_rollback_to_Random"], pre["a3_halves"]["cells"]
    p56 = pre["a3_daypairs"]["2019-11-25→2019-11-26"]
    d45 = dev["a3_daypairs"]["2019-11-24→2019-11-25"]
    checks = []

    def add(name, ours, committed, rel, source):
        ok = abs(ours - committed) <= rel * max(abs(ours), abs(committed), 1e-300)
        checks.append(dict(check=name, ours=ours, committed=committed, rel_tol=rel, ok=bool(ok), source=source))

    def far(pid, src):
        return series[(pid, src)]["rows"][-1 if src == "SB" else 0]

    def after(pid, src, rec, cells, logging_cell, src_label, gate_case=None, ess_n=None):
        r = far(pid, src)
        for e in EST:
            add(f"{pid} {src} far-end {e} value", r[e]["v"], cells[logging_cell]["v"] - rec[e]["policy_effect_after"], 1e-9, f"{src_label} {e}.policy_effect_after")
        if gate_case:
            g = gp[gate_case]
            add(f"{pid} {src} far-end ESS/n", r["ess_frac"], g["ess_frac"], 1e-6, f"gate_obd_posthoc.json '{gate_case}' ess_frac")
            add(f"{pid} {src} far-end mean-weight z", r["z"], g["z_mean_w"], 1e-6, f"gate_obd_posthoc.json '{gate_case}' z_mean_w")
        if ess_n is not None:
            add(f"{pid} {src} far-end ESS", r["ess"], ess_n, 1e-9, f"{src_label} ess")

    def before(pid, src, rec, cells, logging_cell, src_label, ess_n):
        r = far(pid, src)
        for e in EST:
            add(f"{pid} {src} far-end {e} value", r[e]["v"], cells[logging_cell]["v"] + rec[e]["policy_effect_after"] - rec[e]["interaction"], 1e-9,
                f"{src_label} {e}: {logging_cell} + policy_effect_after − interaction")
        add(f"{pid} {src} far-end ESS", r["ess"], ess_n, 1e-9, f"{src_label} ess_before")

    after("W2", "SB", hA, hc, "B2", "obd_slice.json a3_halves.A_deploy_BTS", "halves · A deploy BTS", hA["ess_after"])
    after("D26", "SB", p56["A_deploy_BTS"], p56["cells"], "B2", "obd_slice.json a3_daypairs[25→26].A_deploy_BTS", "2019-11-25→2019-11-26 · A deploy BTS", p56["A_deploy_BTS"]["ess_after"])
    after("D25", "SB", d45["A_deploy_BTS"], d45["cells"], "B2", "obd_slice_deviation_floor.json a3_daypairs[24→25].A_deploy_BTS", "2019-11-24→2019-11-25 · A deploy BTS", d45["A_deploy_BTS"]["ess_after"])
    before("W1", "SB", hB, hc, "B1", "obd_slice.json a3_halves.B_rollback_to_Random", hB["ess_before"])
    before("D24", "SB", d45["B_rollback_to_Random"], d45["cells"], "B1", "obd_slice_deviation_floor.json a3_daypairs[24→25].B_rollback_to_Random", d45["B_rollback_to_Random"]["ess_before"])
    r = far("W", "SR")
    for e in EST:
        add(f"W SR far-end {e} value", r[e]["v"], pre["a2"]["P-hourly"][e]["value"], 1e-9, f"obd_slice.json a2.P-hourly.{e}.value")
    add("W SR far-end ESS", r["ess"], pre["a2"]["P-hourly"]["ess"], 1e-9, "obd_slice.json a2.P-hourly.ess")
    g = gp["Analysis 2 Random→V(BTS) P-hourly"]
    add("W SR far-end mean-weight z", r["z"], g["z_mean_w"], 1e-6, "gate_obd_posthoc.json 'Analysis 2 Random→V(BTS) P-hourly' z_mean_w")
    after("W2", "SR", hB, hc, "R2", "obd_slice.json a3_halves.B_rollback_to_Random", "halves · B roll back", hB["ess_after"])
    after("D26", "SR", p56["B_rollback_to_Random"], p56["cells"], "R2", "obd_slice.json a3_daypairs[25→26].B_rollback_to_Random", "2019-11-25→2019-11-26 · B roll back", p56["B_rollback_to_Random"]["ess_after"])
    after("D25", "SR", d45["B_rollback_to_Random"], d45["cells"], "R2", "obd_slice_deviation_floor.json a3_daypairs[24→25].B_rollback_to_Random", "2019-11-24→2019-11-25 · B roll back", d45["B_rollback_to_Random"]["ess_after"])
    before("W1", "SR", hA, hc, "R1", "obd_slice.json a3_halves.A_deploy_BTS", hA["ess_before"])
    before("D24", "SR", d45["A_deploy_BTS"], d45["cells"], "R1", "obd_slice_deviation_floor.json a3_daypairs[24→25].A_deploy_BTS", d45["A_deploy_BTS"]["ess_before"])
    # CTR cells used by the reference line
    for pid, src, cells, cb, cr, lab in (("W2", "SB", hc, "B2", "R2", "a3_halves"), ("W1", "SB", hc, "B1", "R1", "a3_halves"),
                                          ("D26", "SB", p56["cells"], "B2", "R2", "a3_daypairs[25→26]"), ("D25", "SB", p56["cells"], "B1", "R1", "a3_daypairs[25→26]"),
                                          ("D24", "SB", d45["cells"], "B1", "R1", "deviation a3_daypairs[24→25]")):
        s = series[(pid, src)]
        add(f"{pid} BTS-arm CTR", s["log"]["Sr"] / s["log"]["n"], cells[cb]["v"], 1e-12, f"{lab}.cells.{cb}.v")
        add(f"{pid} Random-arm CTR", s["other"]["Sr"] / s["other"]["n"], cells[cr]["v"], 1e-12, f"{lab}.cells.{cr}.v")
    s = series[("W", "SB")]
    add("W BTS-arm CTR", s["log"]["Sr"] / s["log"]["n"], pre["a2"]["truth"], 1e-12, "obd_slice.json a2.truth")
    add("W Random-arm CTR", s["other"]["Sr"] / s["other"]["n"], pre["a2"]["random_ctr"], 1e-12, "obd_slice.json a2.random_ctr")
    # committed (500-draw bootstrap) far-end S1 intervals next to ours (reported, not a pass/fail check)
    side = []
    for pid, src, rec, lab in (("W2", "SB", hA, "halves A"), ("D26", "SB", p56["A_deploy_BTS"], "25→26 A"), ("D25", "SB", d45["A_deploy_BTS"], "dev 24→25 A"),
                               ("W2", "SR", hB, "halves B"), ("D26", "SR", p56["B_rollback_to_Random"], "25→26 B"), ("D25", "SR", d45["B_rollback_to_Random"], "dev 24→25 B")):
        r = far(pid, src)
        for e in EST:
            dd = -(r[e]["v"] - r["ref"])  # committed sign: (policy effect estimate − reference) = −(V̂ − reference)
            side.append(dict(series=f"{pid}·{src}", estimator=e, committed_lo=rec[e]["minus_truth_lo"], committed_hi=rec[e]["minus_truth_hi"],
                             committed_S1=rec[e]["S1_ci_contains_0"], ours_lo=dd - Z * r[e]["d_se"], ours_hi=dd + Z * r[e]["d_se"], ours_E2=r[e]["E2"], source=lab))
    r = far("W", "SR")
    for e in EST:
        a2e = pre["a2"]["P-hourly"][e]
        side.append(dict(series="W·SR", estimator=e, committed_lo=a2e["diff_lo"], committed_hi=a2e["diff_hi"], committed_S1=a2e["consistent"],
                         ours_lo=(r[e]["v"] - r["ref"]) - Z * r[e]["d_se"], ours_hi=(r[e]["v"] - r["ref"]) + Z * r[e]["d_se"], ours_E2=r[e]["E2"],
                         source="a2 P-hourly (sign: V̂ − reference)"))
    return checks, side


def crosscheck(series, rule):
    """Closed forms vs gate.py diagnostics() and per-row arrays at 11 alphas per series (pass/fail only: deterministic)."""
    out = {}
    for key, s in series.items():
        L, x = s["_rows"]
        xr = np.repeat(x, L["k"])
        rr = np.repeat(L["click"].astype(float), L["k"])
        ok = True
        for a in CHECK_ALPHAS:
            lam = a if s["source"] == "SB" else 1.0 - a
            w = (1.0 - lam) + lam * xr
            dg = diagnostics(w, rr)
            r = next(c for c in s["rows"] if abs(c["a"] - a) < 1e-12)
            ok &= math.isclose(dg["ess_frac"], r["ess_frac"], rel_tol=1e-9)
            ok &= math.isclose(dg["ess_r"], r["ess_r"], rel_tol=1e-9)
            ok &= math.isclose(dg["z_mean_w"], r["z"], rel_tol=1e-9, abs_tol=1e-9)
            ok &= math.isclose(dg["max_w"], r["max_w"], rel_tol=1e-12)
            ok &= decide(dg, rule)[0] == r["answer"]
            wr = w * rr
            ok &= math.isclose(float(wr.mean()), r["IPW"]["v"], rel_tol=1e-9)
            ok &= math.isclose(float(wr.std(ddof=1) / math.sqrt(len(wr))), r["IPW"]["se"], rel_tol=1e-7)
            v = float(wr.sum() / w.sum())
            phi = v + w * (rr - v) / w.mean()
            ok &= math.isclose(v, r["SNIPW"]["v"], rel_tol=1e-9)
            ok &= math.isclose(float(phi.std(ddof=1) / math.sqrt(len(phi))), r["SNIPW"]["se"], rel_tol=1e-7)
        out[f"{key[0]}·{key[1]}"] = bool(ok)
        del xr, rr
    return out


def k3(x):
    return f"{1000 * x:.3f}"


def write_summary(res, path):
    L = ["# α-knob — results (REAL data; pre-registered)", "",
         f"Implements [`preregistration_knob.md`](../preregistration_knob.md) (commit `{PREREG['commit'][:7]}`, registered {PREREG['registered_at']}, before any knob computation). "
         "Reproduce: `python3 demo/knob.py` (numpy). Units: clicks per 1,000 impressions. Candidate π_α = (1 − α)·BTS + α·uniform. "
         "Reference = (1 − α)·CTR(BTS arm) + α·CTR(Random arm), same period: the **concurrent A/B reference**, not ground truth (arm-balance label artefact unresolved). "
         "Gate: frozen `eval/gate_rule.json` via `components/report/gate.py`.", "",
         f"**Integrity:** extract sha256 matches the manifest; reproduction checks {sum(c['ok'] for c in res['reproduction'])}/{len(res['reproduction'])} pass; "
         f"closed forms vs gate.py/per-row arrays {sum(res['crosscheck'].values())}/{len(res['crosscheck'])} series pass.", ""]
    L += ["## Per-series summary — IPW, row-level interval (registered primary = the BTS-logs rows)", "",
          "Scan away from the logging policy (BTS logs: α from 0 up; Random logs: α from 1 down). 101 grid points per row. "
          "E1 = reference inside the 95% CI. *Answered miss* = gate answers and E1 fails; *unnecessary abstention* = gate abstains and E1 holds.", "",
          "| period | logs | gate first abstains at α | E1 first fails at α | answered ✓ | answered miss | unnecessary abstention | justified abstention | largest answered miss (per 1,000) |",
          "|---|---|---|---|---|---|---|---|---|"]
    for k, s in res["series"].items():
        sm, e1 = s["summary"], s["summary"]["IPW_row"]["E1"]
        fa = "never" if sm["first_abstain"] is None else f"{sm['first_abstain']:.2f}"
        ff = "never" if e1["first_fail"] is None else f"{e1['first_fail']:.2f}"
        L.append(f"| {s['label']} | {'BTS (exact)' if s['source'] == 'SB' else 'Random (approx. target)'} | {fa} | {ff} | {e1['answered_hold']} | {e1['answered_miss']} | "
                 f"{e1['unnecessary_abstention']} | {e1['justified_abstention']} | {k3(e1['max_answered_miss'])} |")
    cats = ("answered_hold", "answered_miss", "unnecessary_abstention", "justified_abstention")

    def tsum(src, key, ep):
        return {c: sum(s["summary"][key][ep][c] for s in res["series"].values() if src in (None, s["source"])) for c in cats}
    p1, p2, sr, pool = tsum("SB", "IPW_row", "E1"), tsum("SB", "IPW_row", "E2"), tsum("SR", "IPW_row", "E1"), tsum(None, "IPW_row", "E1")
    n_sb = sum(len(s["rows"]) for s in res["series"].values() if s["source"] == "SB")
    n_sr = sum(len(s["rows"]) for s in res["series"].values() if s["source"] == "SR")
    sb_ans = [r for s in res["series"].values() if s["source"] == "SB" for r in s["rows"] if r["answer"]]
    n0, nz = sum(r["a"] == 0 for r in sb_ans), [r for r in sb_ans if r["a"] > 0]
    L += ["", f"**Registered primary (IPW, row-level, BTS logs; {n_sb} grid points):** the gate answered {p1['answered_hold'] + p1['answered_miss']}/{n_sb}; "
              f"E1 held at {p1['answered_hold']}/{p1['answered_hold'] + p1['answered_miss']} answered ({p1['answered_miss']} answered misses). "
              f"Of those answers, {n0} are at α = 0, the logging end, where the estimate equals the reference by construction; "
              f"at α > 0, E1 held at {sum(bool(r['IPW']['E1']) for r in nz)}/{len(nz)}. "
              f"It refused {p1['unnecessary_abstention'] + p1['justified_abstention']}/{n_sb} ({p1['unnecessary_abstention']} with the reference inside the own CI, "
              f"{p1['justified_abstention']} outside). Ungated IPW on the same points: E1 holds at {p1['answered_hold'] + p1['unnecessary_abstention']}/{n_sb}. "
              f"E2 on the same scope: answered {p2['answered_hold']} consistent, {p2['answered_miss']} rejecting; refused {p2['unnecessary_abstention']} consistent, "
              f"{p2['justified_abstention']} rejecting.",
          f"**Secondary — Random logs (approximate target; {n_sr} grid points):** answered {sr['answered_hold'] + sr['answered_miss']}/{n_sr}; "
              f"E1 held at {sr['answered_hold']}/{sr['answered_hold'] + sr['answered_miss']} answered.",
          f"**Secondary — pooled over both sources (not the registered primary; 12 series × 101 points):** answered ✓ {pool['answered_hold']}, "
              f"answered miss {pool['answered_miss']}, unnecessary abstention {pool['unnecessary_abstention']}, justified abstention {pool['justified_abstention']}.",
          "All counts are correlated grid locations from overlapping periods and deterministic α steps, not independent decisions.", ""]
    L += ["## Secondary summaries — every estimator, endpoint and interval", "",
          "Format: answered ✓ / answered miss / unnecessary abstention / justified abstention (first failing α).", "",
          "| period | logs | IPW E1 row | IPW E1 hour-cluster | IPW E2 row | IPW E2 hour-cluster | SNIPW E1 row | SNIPW E1 hour-cluster | SNIPW E2 row | SNIPW E2 hour-cluster |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for k, s in res["series"].items():
        cells = []
        for e in EST:
            for ep in ("E1", "E2"):
                for iv in ("row", "cluster"):
                    q = s["summary"][f"{e}_{iv}"][ep]
                    ff = "–" if q["first_fail"] is None else f"{q['first_fail']:.2f}"
                    cells.append((e, ep, iv, f"{q['answered_hold']}/{q['answered_miss']}/{q['unnecessary_abstention']}/{q['justified_abstention']} ({ff})"))
        order = [("IPW", "E1", "row"), ("IPW", "E1", "cluster"), ("IPW", "E2", "row"), ("IPW", "E2", "cluster"),
                 ("SNIPW", "E1", "row"), ("SNIPW", "E1", "cluster"), ("SNIPW", "E2", "row"), ("SNIPW", "E2", "cluster")]
        cm = {(a, b, c): t for a, b, c, t in cells}
        L.append(f"| {s['period']} | {s['source']} | " + " | ".join(cm[o] for o in order) + " |")
    L += ["", "## Pre-registered predictions vs results", "", "| series | item | predicted | result | grade |", "|---|---|---|---|---|"]
    for k, g in res["predictions"].items():
        if "grade" in g:
            L.append(f"| {k} | all | {g['predicted']} | {g['result']} | {g['grade']} |")
            continue
        for item, v in g.items():
            L.append(f"| {k} | {item} | {v['predicted']} | {v['result']} | {v['grade']} |")
    L += ["", "**P1 (logging end exact) and P2 (algebra):**", "", "| series | P1 | IPW gap linear in λ | abs(z) constant for λ > 0 | IPW E2 constant | IPW E1 crosses at most once |", "|---|---|---|---|---|---|"]
    for k, v in res["p1_p2"].items():
        yn = lambda b: "yes" if b else "NO"
        L.append(f"| {k} | {yn(v['P1_logging_end_exact'])} | {yn(v['P2_ipw_gap_linear'])} | {yn(v['P2_abs_z_constant'])} | {yn(v['P2_E2_ipw_constant'])} | {yn(v['P2_E1_ipw_single_crossing'])} |")
    L += ["", "## Key grid points", "", "Value ± 95% half-width (row-level), per 1,000. Gate: ✓ answer, ✗ can't tell (reason).", "",
          "| period | logs | α | reference | IPW | SNIPW | ESS/n | effective rows | mean-weight z | gate |", "|---|---|---|---|---|---|---|---|---|---|"]
    for k, s in res["series"].items():
        for r in s["rows"]:
            if round(r["a"] * 100) % 25 == 0:
                gate = "✓" if r["answer"] else "✗ " + "; ".join(r["why"]).replace("|", "\\|")
                L.append(f"| {s['period']} | {s['source']} | {r['a']:.2f} | {k3(r['ref'])} ± {k3(Z * r['se_ref'])} | {k3(r['IPW']['v'])} ± {k3(Z * r['IPW']['se'])}{'' if r['IPW']['E1'] else ' (ref outside)'} | "
                         f"{k3(r['SNIPW']['v'])} ± {k3(Z * r['SNIPW']['se'])}{'' if r['SNIPW']['E1'] else ' (ref outside)'} | {r['ess_frac']:.4f} | {r['ess']:,.0f} | {r['z']:+.2f} | {gate} |")
    L += ["", "## Reproduction checks (far-end cells and CTRs vs committed results)", "", "| check | ours | committed | tolerance | ok | source |", "|---|---|---|---|---|---|"]
    for c in res["reproduction"]:
        L.append(f"| {c['check']} | {c['ours']!r} | {c['committed']!r} | {c['rel_tol']:g} | {'yes' if c['ok'] else 'NO'} | {c['source']} |")
    L += ["", "**Committed far-end S1 intervals (500-draw bootstrap SE) next to ours (analytic SE)** — same quantity, (estimate − reference) in committed sign convention, per 1,000:", "",
          "| series | estimator | committed CI | committed S1 | our CI | our E2 |", "|---|---|---|---|---|---|"]
    for c in res["far_end_intervals"]:
        L.append(f"| {c['series']} | {c['estimator']} | [{k3(c['committed_lo'])}, {k3(c['committed_hi'])}] | {'yes' if c['committed_S1'] else 'NO'} | "
                 f"[{k3(c['ours_lo'])}, {k3(c['ours_hi'])}] | {'yes' if c['ours_E2'] else 'NO'} |")
    path.write_text("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "demo" / "results"))
    ap.add_argument("--no-crosscheck", action="store_true")
    args = ap.parse_args()
    rule = load_rule()
    man, B, R = read_extract()
    pi_h = p_hourly(B)
    series = build_series(B, R, pi_h)
    for s in series.values():
        s["rows"] = [cell(s, a, rule) for a in GRID]
        s["summary"] = summarise(s)
    checks, side = reproduction(series)
    if not all(c["ok"] for c in checks):
        for c in checks:
            if not c["ok"]:
                print("REPRODUCTION FAILED:", c, file=sys.stderr)
        sys.exit("reproduction checks failed — stopping (pre-registration §10)")
    xc = {f"{k[0]}·{k[1]}": None for k in series} if args.no_crosscheck else crosscheck(series, rule)
    res = {"prereg": PREREG, "rule": rule, "grid": GRID, "z": Z,
           "extract": {k: v["sha256"] for k, v in man["files"].items()},
           "periods": [{"id": p[0], "label": p[1], "hours": [p[2], p[3]], "random_pre_t0_rows_included": p[4]} for p in PERIODS],
           "sources": SOURCES, "reproduction": checks, "far_end_intervals": side, "crosscheck": xc, "series": {}}
    for (pid, src), s in series.items():
        res["series"][f"{pid}·{src}"] = {"period": pid, "label": s["label"], "source": src, "source_label": SOURCES[src],
                                        "n_logging": s["log"]["n"], "n_other": s["other"]["n"], "clicks_logging": s["log"]["Sr"], "clicks_other": s["other"]["Sr"],
                                        "max_far_weight": s["log"]["max_x"], "hours": len(s["hours"]), "rows": s["rows"], "summary": s["summary"]}
    res["predictions"] = grade_predictions(series)
    res["p1_p2"] = p1_p2(series)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "knob_results.json").write_text(json.dumps(res, indent=None, separators=(",", ":"), allow_nan=False) + "\n")
    write_summary(res, out / "knob_summary.md")
    print((out / "knob_summary.md").read_text().split("## Secondary")[0])
    print("crosscheck:", xc)
    if not args.no_crosscheck and not all(xc.values()):
        sys.exit("closed-form vs gate.py cross-check FAILED")


if __name__ == "__main__":
    main()
