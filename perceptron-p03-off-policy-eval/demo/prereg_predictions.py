"""Predictions for the pre-registered alpha-knob analysis, derived ONLY from committed results (reads no data).

Reproduce (from perceptron-p03-off-policy-eval/):  python3 demo/prereg_predictions.py
Inputs: eval/results/obd_slice.json, obd_slice_deviation_floor.json, gate_obd_posthoc.json, demo_verdicts.md (W1 |z|).
Standard library only. Writes nothing; its printed table is pasted into demo/preregistration_knob.md.

Model (see the pre-registration): candidate pi_a = (1-a) BTS + a uniform. A "series" is (period, log source).
lam = share of the far-end target in the weights: BTS logs lam = a; Random logs lam = 1 - a.
w = (1 - lam) + lam * x, where x is the far-end weight (BTS logs: (1/80)/ps; Random logs: pi_hourly/0.0125).
Exact consequences used here: IPW(lam) - ref(lam) = lam * (IPW_far - ref_far); |mean-weight z| is constant for lam > 0;
ESS/n(lam) = ((1-lam) + lam m1)^2 / ((1-lam)^2 + 2 lam (1-lam) m1 + lam^2 m2) with m1 = mean(x), m2 = mean(x^2).
m1, m2 are recovered from the committed far-end ESS/n and z; interval widths use the committed (bootstrap) far-end SE,
so the predicted crossings are approximate.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "eval" / "results"
Z = 1.959963984540054
TAU_ESS, TAU_Z = 0.05, 3.0  # eval/gate_rule.json (frozen, b4e95ae)
GRID = [i / 100 for i in range(101)]


def load(name):
    return json.loads((RES / name).read_text())


def se_from_diff(rec_e, se_ref):
    """se of the off-policy value from the committed CI of (estimate - truth) = hypot(se_value, se_ref)."""
    d_se = (rec_e["minus_truth_hi"] - rec_e["minus_truth_lo"]) / (2 * Z)
    return math.sqrt(max(d_se ** 2 - se_ref ** 2, 0.0))


def far_after(rec, cells, logging, other, e="IPW"):
    """Off-policy cell of an 'after' period: V_hat(old) on the new arm's rows. pe = mean(r) - V_hat."""
    r = rec[e]
    v_hat = cells[f"{logging}2"]["v"] - r["policy_effect_after"]
    return dict(v_hat=v_hat, se=se_from_diff(r, cells[f"{other}2"]["se"]), p=cells[f"{logging}2"]["v"],
                q=cells[f"{other}2"]["v"], se_q=cells[f"{other}2"]["se"], s1=r["S1_ci_contains_0"])


def far_before(rec, cells, logging, other, n, e="IPW"):
    """Off-policy cell of a 'before' period, backed out of the committed Shapley fields: pb = pe - interaction."""
    r = rec[e]
    pb = r["policy_effect_after"] - r["interaction"]
    pb_se = math.sqrt(max((2 * r["shapley_policy_se"]) ** 2 - r["se"] ** 2, 0.0))  # se of mean(x r - r) on these rows
    p = cells[f"{logging}1"]["v"]
    v_hat = p + pb
    var_xr = n * pb_se ** 2 + 2 * v_hat * (1 - p) - p * (1 - p)  # Var(xr - r) = Var(xr) - 2 Cov(xr, r) + Var(r)
    return dict(v_hat=v_hat, se=math.sqrt(max(var_xr, 0.0) / n), p=p, q=cells[f"{other}1"]["v"], se_q=cells[f"{other}1"]["se"], s1=None)


def ess_curve(ess1, z1, n):
    c2 = 1.0 / ess1 - 1.0
    m1 = 1.0 / (1.0 - (z1 if z1 is not None else 0.0) * math.sqrt(c2) / math.sqrt(n))
    m2 = m1 ** 2 * (1.0 + c2)
    return lambda lam: ((1 - lam) + lam * m1) ** 2 / ((1 - lam) ** 2 + 2 * lam * (1 - lam) * m1 + lam ** 2 * m2)


def predict(name, src, ess1, z1, n, far, z_note=""):
    lam_of = (lambda a: a) if src == "BTS logs" else (lambda a: 1 - a)
    order = GRID if src == "BTS logs" else GRID[::-1]  # scan away from the logging policy
    if z1 is not None and abs(z1) > TAU_Z:
        gate = f"abstain at every grid point except the logging end (abs(z) {abs(z1):.1f} > 3 at the far end{z_note})"
    else:
        f = ess_curve(ess1, z1, n)
        first = next((a for a in order if f(lam_of(a)) < TAU_ESS), None)
        cond = "" if z1 is not None else " [z not committed: conditional on abs(z) <= 3]"
        gate = (f"answers everywhere (ESS/n stays >= {min(f(lam_of(a)) for a in order):.3f})" if first is None
                else f"answers up to alpha {order[order.index(first) - 1]:.2f}, first abstains at alpha {first:.2f}") + cond
    e1 = "n/a"
    if far is not None:
        err1 = far["v_hat"] - far["q"]
        p, v1, var_xr = far["p"], far["v_hat"], n * far["se"] ** 2
        def holds(a):
            lam = lam_of(a)
            var = (1 - lam) ** 2 * p * (1 - p) + 2 * lam * (1 - lam) * v1 * (1 - p) + lam ** 2 * var_xr
            return abs(lam * err1) <= Z * math.sqrt(var / n)
        fail = next((a for a in order if not holds(a)), None)
        e1 = "holds everywhere" if fail is None else f"fails from alpha {fail:.2f} onwards (away from the logging end)"
        e1 += f"; far-end IPW error {1000 * err1:+.3f}/1,000, far-end half-width {1000 * Z * far['se']:.3f}"
        d_hw = Z * math.hypot(far["se"], far["se_q"])
        e2 = "holds at every alpha" if abs(err1) <= d_hw else "fails at every alpha except the logging end"
        if far["s1"] is not None and far["s1"] != (abs(err1) <= d_hw):
            e2 += " (disagrees with committed S1 flag; check)"
    else:
        e2 = "n/a"
    return dict(series=f"{name} · {src}", far_ess=ess1, far_z=z1, gate=gate, e1=e1, e2=e2)


def main():
    pre, dev, gp = load("obd_slice.json"), load("obd_slice_deviation_floor.json"), load("gate_obd_posthoc.json")
    g = {c["case"]: c for c in gp["cases"]}
    hA, hB = pre["a3_halves"]["A_deploy_BTS"], pre["a3_halves"]["B_rollback_to_Random"]
    hcells = pre["a3_halves"]["cells"]
    p56 = pre["a3_daypairs"]["2019-11-25→2019-11-26"]
    d45 = dev["a3_daypairs"]["2019-11-24→2019-11-25"]
    rows = []
    # ---- BTS logs (exact weights), far end alpha = 1 (uniform target) ----
    c = g["halves · A deploy BTS"]
    rows.append(predict("W2", "BTS logs", c["ess_frac"], c["z_mean_w"], c["n"], far_after(hA, hcells, "B", "R")))
    c = g["2019-11-25→2019-11-26 · A deploy BTS"]
    rows.append(predict("Nov 26", "BTS logs", c["ess_frac"], c["z_mean_w"], c["n"], far_after(p56["A_deploy_BTS"], p56["cells"], "B", "R")))
    c = g["2019-11-24→2019-11-25 · A deploy BTS"]
    rows.append(predict("Nov 25", "BTS logs", c["ess_frac"], c["z_mean_w"], c["n"], far_after(d45["A_deploy_BTS"], d45["cells"], "B", "R")))
    n = hB["n_before"]
    rows.append(predict("W1", "BTS logs", hB["ess_before"] / n, 6.1, n, far_before(hB, hcells, "B", "R", n),
                        z_note="; abs(z) from demo_verdicts.md, sign not recorded"))
    n = d45["B_rollback_to_Random"]["n_before"]
    rows.append(predict("Nov 24", "BTS logs", d45["B_rollback_to_Random"]["ess_before"] / n, None, n,
                        far_before(d45["B_rollback_to_Random"], d45["cells"], "B", "R", n)))
    rows.append(dict(series="W · BTS logs", far_ess=None, far_z=None, gate="not predicted (no committed far-end cell)", e1="not predicted", e2="not predicted"))
    # ---- Random logs (P-hourly reconstruction; approximate target), far end alpha = 0 (BTS target) ----
    a2 = pre["a2"]
    c = g["Analysis 2 Random→V(BTS) P-hourly"]
    far = dict(v_hat=a2["P-hourly"]["IPW"]["value"], se=a2["P-hourly"]["IPW"]["se"], p=a2["random_ctr"], q=a2["truth"], se_q=a2["truth_se"],
               s1=a2["P-hourly"]["IPW"]["consistent"])
    rows.append(predict("W", "Random logs", c["ess_frac"], c["z_mean_w"], c["n"], far))
    c = g["halves · B roll back"]
    rows.append(predict("W2", "Random logs", c["ess_frac"], c["z_mean_w"], c["n"], far_after(hB, hcells, "R", "B")))
    c = g["2019-11-25→2019-11-26 · B roll back"]
    rows.append(predict("Nov 26", "Random logs", c["ess_frac"], c["z_mean_w"], c["n"], far_after(p56["B_rollback_to_Random"], p56["cells"], "R", "B")))
    c = g["2019-11-24→2019-11-25 · B roll back"]
    rows.append(predict("Nov 25", "Random logs", c["ess_frac"], c["z_mean_w"], c["n"], far_after(d45["B_rollback_to_Random"], d45["cells"], "R", "B")))
    n = hA["n_before"]
    r_w1 = predict("W1", "Random logs", hA["ess_before"] / n, None, n, far_before(hA, hcells, "R", "B", n))
    r_w1["gate"] += " [committed: passed the gate at the far end, demo_verdicts.md]"
    rows.append(r_w1)
    n = d45["A_deploy_BTS"]["n_before"]
    rows.append(predict("Nov 24", "Random logs", d45["A_deploy_BTS"]["ess_before"] / n, None, n,
                        far_before(d45["A_deploy_BTS"], d45["cells"], "R", "B", n)))
    print("| series | far-end ESS/n (committed) | far-end z (committed) | predicted gate | predicted E1 (IPW, row-level) | predicted E2 (IPW) |")
    print("|---|---|---|---|---|---|")
    for r in rows:
        ess = "—" if r["far_ess"] is None else f"{r['far_ess']:.6f}"
        z = "—" if r["far_z"] is None else (f"abs {r['far_z']:.1f} (sign not recorded)" if "sign not recorded" in r["gate"] else f"{r['far_z']:+.3f}")
        print(f"| {r['series']} | {ess} | {z} | {r['gate']} | {r['e1']} | {r['e2']} |")


if __name__ == "__main__":
    main()
