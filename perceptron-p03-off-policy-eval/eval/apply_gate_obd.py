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
    for pol, (w, r) in (("P-static", (w_s, Rw["click"].astype(float))), ("P-hourly", w_hourly_on_random(Rw, pi_h))):
        ok = pre["a2"][pol]["DR"]["consistent"]
        cases.append(("pre-registered", f"Analysis 2 Random→V(BTS) {pol}", w, r, ok))
    t_mid = t0_pre + (t_end - t0_pre) // 2
    cases.append(("pre-registered", "halves · A deploy BTS", *w_uniform_on_bts(sub(Bw, Bw["ts"] >= t_mid)), pre["a3_halves"]["A_deploy_BTS"]["DR"]["S1_ci_contains_0"]))
    cases.append(("pre-registered", "halves · B roll back", *w_hourly_on_random(sub(Rw, Rw["ts"] >= t_mid), pi_h), pre["a3_halves"]["B_rollback_to_Random"]["DR"]["S1_ci_contains_0"]))
    # deviation window: whole-day pairs (the after-day logs decide the gate)
    Rw, Bw, pi_h = window((t0_pre // HOUR) * HOUR)
    for lab, p in dev["a3_daypairs"].items():
        d2 = np.datetime64(lab.split("→")[1], "D").astype("datetime64[ns]").astype(np.int64) // (24 * HOUR)
        cases.append(("deviation", f"{lab} · A deploy BTS", *w_uniform_on_bts(sub(Bw, Bw["ts"] // (24 * HOUR) == d2)), p["A_deploy_BTS"]["DR"]["S1_ci_contains_0"]))
        cases.append(("deviation", f"{lab} · B roll back", *w_hourly_on_random(sub(Rw, Rw["ts"] // (24 * HOUR) == d2), pi_h), p["B_rollback_to_Random"]["DR"]["S1_ci_contains_0"]))

    rows, out = [], []
    for src, name, w, r, truth_ok in cases:
        dg = diagnostics(w, r)
        answer, why = decide(dg, rule)
        verdict = ("answered, correct" if truth_ok else "answered, WRONG (CI missed truth)") if answer else (
            "abstained (would have been right)" if truth_ok else "abstained (would have been wrong)")
        out.append(dict(source=src, case=name, answer=answer, dr_ci_contains_truth=bool(truth_ok), verdict=verdict, **dg))
        rows.append(f"| {src} | {name} | {dg['ess_frac']:.4f} | {dg['ess_r']:.0f} | {dg['z_mean_w']:+.1f} | {'answer' if answer else 'ABSTAIN: ' + '; '.join(why)} | {'yes' if truth_ok else 'NO'} | {verdict} |")
    n_ans = sum(o["answer"] for o in out)
    n_wrong = sum(o["answer"] and not o["dr_ci_contains_truth"] for o in out)
    n_abst_bad = sum((not o["answer"]) and not o["dr_ci_contains_truth"] for o in out)
    n_bad = sum(not o["dr_ci_contains_truth"] for o in out)
    summary = {"rule": rule, "cases": len(out), "answered": n_ans, "answered_wrong": n_wrong, "failures_total": n_bad,
               "failures_abstained": n_abst_bad, "abstained_but_right": sum((not o["answer"]) and o["dr_ci_contains_truth"] for o in out)}
    L = ["# POST-HOC — frozen overlap gate applied to the real OBD cases", "",
         f"Rule (from `eval/gate_rule.json`, calibrated on the simulator only at {rule['calibrated_at']}, commit b4e95ae): abstain if ESS/n < {rule['tau_ess']} "
         f"or effective rewards < {rule['tau_r']:.0f} or |mean-weight z| > {rule['tau_z']}. "
         "**Post hoc:** the OBD outcomes and ESS values below were seen before the gate was calibrated.", "",
         f"**Result:** {n_ans} of {len(out)} cases answered, {n_wrong} of them wrong. "
         f"{n_abst_bad} of the {n_bad} cases where DR's interval missed the truth were abstained on. "
         f"Cost: {summary['abstained_but_right']} abstention(s) where DR would have been right.", "",
         "| source | case | ESS/n | effective rewards | mean-weight z | gate | DR CI ∋ truth | verdict |", "|---|---|---|---|---|---|---|---|"] + rows
    (RES / "gate_obd_posthoc.md").write_text("\n".join(L) + "\n")
    (RES / "gate_obd_posthoc.json").write_text(json.dumps({"summary": summary, "cases": out}, indent=1, default=float))
    print("\n".join(L))


if __name__ == "__main__":
    main()
