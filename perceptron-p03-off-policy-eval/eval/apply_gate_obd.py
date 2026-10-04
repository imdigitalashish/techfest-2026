"""POST-HOC: apply the frozen overlap gate (eval/gate_rule.json, calibrated on the simulator only, committed 13:39:56 IST
in b4e95ae) to every real OBD case. Disclosure: the OBD outcomes (DR interval contains the truth or not) and the
ESS/n values were seen BEFORE the gate was calibrated; the calibration code never reads OBD, but this check is post hoc.

Reproduce: cd perceptron-p03-off-policy-eval && nice -n 10 .venv/bin/python eval/apply_gate_obd.py
Writes eval/results/gate_obd_posthoc{.md,.json}.
"""
from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "eval"))
from components.report.gate import decide, diagnostics, load_rule  # noqa: E402
from run_obd_slice import HOUR, S, bts_action_dist, load, sub  # noqa: E402

RES = ROOT / "eval" / "results"


def main():
    rule = load_rule()
    pre = json.loads((RES / "obd_slice.json").read_text())
    dev = json.loads((RES / "obd_slice_deviation_floor.json").read_text())
    R, B = load(S / "random" / "all" / "all.npz"), load(S / "bts" / "all" / "all.npz")
    n_items = 80
    t0_pre = max(R["ts"].min(), B["ts"].min())
    t_end = (B["ts"].max() // HOUR) * HOUR
    cases = []

    def window(t0):
        Rw, Bw = sub(R, (R["ts"] >= t0) & (R["ts"] < t_end)), sub(B, (B["ts"] >= t0) & (B["ts"] < t_end))
        h0 = t0 // HOUR
        Rw["h"], Bw["h"] = Rw["ts"] // HOUR - h0, Bw["ts"] // HOUR - h0
        H = int(max(Rw["h"].max(), Bw["h"].max())) + 1
        cnt = np.zeros((H, n_items, 3))
        np.add.at(cnt, (Bw["h"], Bw["item"].astype(int), Bw["pos"].astype(int) - 1), 1.0)
        tot = cnt.sum(1, keepdims=True)
        return Rw, Bw, np.divide(cnt, tot, out=np.zeros_like(cnt), where=tot > 0)

    def w_uniform_on_bts(Bx):
        return (1.0 / n_items) / Bx["ps"], Bx["click"].astype(float)

    def w_hourly_on_random(Rx, pi_h):
        return pi_h[Rx["h"], Rx["item"].astype(int), Rx["pos"].astype(int) - 1] / Rx["ps"], Rx["click"].astype(float)

    # pre-registered window: Analysis 2 + halves
    Rw, Bw, pi_h = window(t0_pre)
    pi_s = bts_action_dist(n_sim=400_000)
    w_s = pi_s[Rw["item"].astype(int), Rw["pos"].astype(int) - 1] / Rw["ps"]
    Z = 1.959963984540054

    def endpoints(est, se, ref, kind):
        e = {"est": est, "se": se, "ref": ref, "ref_in_ci": abs(est - ref) <= Z * se}
        e["confident_wrong_sign"] = (kind == "effect") and ((est - Z * se > 0 > ref) or (est + Z * se < 0 < ref))
        return e

    for pol, (w, r) in (("P-static", (w_s, Rw["click"].astype(float))), ("P-hourly", w_hourly_on_random(Rw, pi_h))):
        d = pre["a2"][pol]["DR"]
        cases.append(("pre-registered", f"Analysis 2 Random→V(BTS) {pol}", f"A2|{pol}", w, r, d["consistent"],
                      endpoints(d["value"], d["se"], pre["a2"]["truth"], "value")))
    t_mid = t0_pre + (t_end - t0_pre) // 2
    eff = lambda rec: endpoints(rec["DR"]["policy_effect_after"], rec["DR"]["se"], rec["truth"], "effect")
    hA, hB = pre["a3_halves"]["A_deploy_BTS"], pre["a3_halves"]["B_rollback_to_Random"]
    cases.append(("pre-registered", "halves · A deploy BTS", "halves|A", *w_uniform_on_bts(sub(Bw, Bw["ts"] >= t_mid)), hA["DR"]["S1_ci_contains_0"], eff(hA)))
    cases.append(("pre-registered", "halves · B roll back", "halves|B", *w_hourly_on_random(sub(Rw, Rw["ts"] >= t_mid), pi_h), hB["DR"]["S1_ci_contains_0"], eff(hB)))
    # deviation window: whole-day pairs (the after-day logs decide the gate)
    Rw, Bw, pi_h = window((t0_pre // HOUR) * HOUR)
    for lab, p in dev["a3_daypairs"].items():
        d2 = np.datetime64(lab.split("→")[1], "D").astype("datetime64[ns]").astype(np.int64) // (24 * HOUR)
        aday = lab.split("→")[1]
        cases.append(("deviation", f"{lab} · A deploy BTS", f"day|A|after {aday}", *w_uniform_on_bts(sub(Bw, Bw["ts"] // (24 * HOUR) == d2)),
                      p["A_deploy_BTS"]["DR"]["S1_ci_contains_0"], eff(p["A_deploy_BTS"])))
        cases.append(("deviation", f"{lab} · B roll back", f"day|B|pair {lab}", *w_hourly_on_random(sub(Rw, Rw["ts"] // (24 * HOUR) == d2), pi_h),
                      p["B_rollback_to_Random"]["DR"]["S1_ci_contains_0"], eff(p["B_rollback_to_Random"])))

    rows, out = [], []
    for src, name, key, w, r, s1, ep in cases:
        dg = diagnostics(w, r)
        answer, why = decide(dg, rule)
        out.append(dict(source=src, case=name, unique_key=key, answer=answer, s1_nonrejection=bool(s1),
                        ref_in_dr_ci=bool(ep["ref_in_ci"]), confident_wrong_sign=bool(ep["confident_wrong_sign"]),
                        est=ep["est"], se=ep["se"], ref=ep["ref"], ess_abs=dg["ess_frac"] * dg["n"], **dg))
        rows.append(f"| {src} | {name} | {dg['ess_frac']:.4f} | {dg['ess_frac'] * dg['n']:,.0f} | {dg['z_mean_w']:+.1f} | "
                    f"{'answer' if answer else 'ABSTAIN: ' + '; '.join(why)} | {'yes' if s1 else 'NO'} | {'yes' if ep['ref_in_ci'] else 'NO'} | "
                    f"{'YES' if ep['confident_wrong_sign'] else 'no'} |")
    def summ(xs):
        ans = [x for x in xs if x["answer"]]
        abst = [x for x in xs if not x["answer"]]
        return {"listed": len(xs), "answered": len(ans), "answered_s1_nonrejection": sum(x["s1_nonrejection"] for x in ans),
                "answered_ref_in_ci": sum(x["ref_in_dr_ci"] for x in ans), "answered_confident_wrong_sign": sum(x["confident_wrong_sign"] for x in ans),
                "abstained": len(abst), "abstained_s1_rejected": sum(not x["s1_nonrejection"] for x in abst),
                "abstained_ref_in_ci": sum(x["ref_in_dr_ci"] for x in abst),
                "s1_rejected_total": sum(not x["s1_nonrejection"] for x in xs)}
    # a repeated after-period estimate (day pairs sharing an after-day) counts once
    by_est = {}
    for o_ in out:
        by_est.setdefault((o_["case"].split(" · ")[-1], round(o_["est"], 12), round(o_["ref"], 12)), o_)
    summary = {"rule": rule, "rows": summ(out), "unique_instances": summ(list(by_est.values())),
               "note": "unique = distinct (direction, estimate, reference): day pairs sharing an after-day are one instance"}
    U, Rw_ = summary["unique_instances"], summary["rows"]
    L = ["# POST-HOC — frozen overlap gate applied to the real OBD cases (endpoints separated per review A1/A6)", "",
         f"Rule (from `eval/gate_rule.json`, calibrated on the simulator only at {rule['calibrated_at']}, commit b4e95ae): abstain if ESS/n < {rule['tau_ess']} "
         f"or effective rewards < {rule['tau_r']:.0f} (inactive at 0) or |mean-weight z| > {rule['tau_z']}. "
         "**Post hoc and exploratory:** the gate's diagnostics, simulator knobs and selection criterion were chosen after the OBD failures below had been seen.", "",
         "Three endpoints, never merged: **S1** = the pre-registered consistency test (CI of estimate − reference contains 0; a non-rejection, not proof of accuracy); "
         "**ref ∈ CI** = the reference point lies inside DR's own 95% interval; **confident wrong sign** = DR's interval excludes 0 on the opposite side of the reference.", "",
         f"**Listed rows ({Rw_['listed']}):** answered {Rw_['answered']} — S1 non-rejections {Rw_['answered_s1_nonrejection']}/{Rw_['answered']}, "
         f"reference inside DR's CI {Rw_['answered_ref_in_ci']}/{Rw_['answered']}, confident wrong sign {Rw_['answered_confident_wrong_sign']}/{Rw_['answered']}; "
         f"abstained {Rw_['abstained']} (of which S1 rejected {Rw_['abstained_s1_rejected']}).",
         f"**Distinct evaluation instances ({U['listed']}; day pairs sharing an after-day counted once):** answered {U['answered']} — "
         f"S1 {U['answered_s1_nonrejection']}/{U['answered']}, ref ∈ CI {U['answered_ref_in_ci']}/{U['answered']}, confident wrong sign {U['answered_confident_wrong_sign']}/{U['answered']}; "
         f"abstained {U['abstained']}, covering {U['abstained_s1_rejected']} of the {U['s1_rejected_total']} S1 rejections. Instances still share observations.", "",
         "| source | case | ESS/n | ESS (absolute) | mean-weight z | gate | S1 non-rejection | ref ∈ DR CI | confident wrong sign |", "|---|---|---|---|---|---|---|---|---|"] + rows
    (RES / "gate_obd_posthoc.md").write_text("\n".join(L) + "\n")
    (RES / "gate_obd_posthoc.json").write_text(json.dumps({"summary": summary, "cases": out}, indent=1, default=float))
    print("\n".join(L))


if __name__ == "__main__":
    main()
