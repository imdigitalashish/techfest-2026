"""Demo: the verdicts the product would print, on the simulator (SYNTHETIC) and on real OBD re-enacted switches (REAL).

Reproduce: cd perceptron-p03-off-policy-eval && nice -n 10 .venv/bin/python eval/demo_verdicts.py
Writes eval/results/demo_verdicts.md. OBD verdicts reuse the pre-registered estimates in eval/results/obd_slice.json and
gate both off-policy cells with the frozen rule (eval/gate_rule.json) — applying the gate to OBD is POST HOC.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "eval"))

from architecture.contracts.contracts import ActionDist, Interval, ScenarioConfig, ShapleyDecomposition  # noqa: E402
from components.decomposer.decompose import shapley  # noqa: E402
from components.report.gate import diagnostics, load_rule  # noqa: E402
from components.report.verdict import AFTER, BEFORE, verdict  # noqa: E402
from components.sensitivity.msm import delta_curve  # noqa: E402
from components.simulator.sim import World, ground_truth, simulate  # noqa: E402
from run_sim_bank import BANK, COMMON, GAMMAS  # noqa: E402

Z = 1.959963984540054


def sim_cases(rule):
    rows = []
    for name in ("S1_drift_masks_gain", "S2_drift_fakes_gain", "S3_stationary_control", "S5_low_overlap", "S4_hidden_override"):
        cfg = ScenarioConfig(name=name, seed=0, **COMMON, **BANK[name])
        t = ground_truth(World(cfg), n_mc=200_000)
        sim = simulate(cfg, t)
        w = sim.world
        pi_new_b = ActionDist(probs=w.policy(sim.before.X, "new"), policy="new")
        pi_old_a = ActionDist(probs=w.policy(sim.after.X, "old"), policy="old")
        sh = shapley(sim.before, sim.after, pi_new_b, pi_old_a)
        ia, ib = np.arange(len(sim.after.A)), np.arange(len(sim.before.A))
        w_a = pi_old_a.probs[ia, sim.after.A] / sim.after.pscore
        w_b = pi_new_b.probs[ib, sim.before.A] / sim.before.pscore
        diags = {AFTER: diagnostics(w_a, sim.after.R), BEFORE: diagnostics(w_b, sim.before.R)}
        curve = None
        if name == "S4_hidden_override":
            curve = delta_curve(pi_old_a.probs[ia, sim.after.A], sim.after.pscore, sim.after.R, GAMMAS, B=100, seed=0)
        v = verdict(sh, diags, rule, sensitivity=curve)
        rows.append((name, v, f"truth: policy (Shapley) {100 * t.shapley_policy:+.2f}, after-period effect {100 * t.policy_effect_after:+.2f} points"))
    return rows


def obd_cases(rule):
    o = json.loads((ROOT / "eval" / "results" / "obd_slice.json").read_text())
    g = {c["case"]: c for c in json.loads((ROOT / "eval" / "results" / "gate_obd_posthoc.json").read_text())["cases"]}
    from run_obd_slice import HOUR, S, load, sub
    R, B = load(S / "random" / "all" / "all.npz"), load(S / "bts" / "all" / "all.npz")
    t0, t_end = max(R["ts"].min(), B["ts"].min()), (B["ts"].max() // HOUR) * HOUR
    t_mid = t0 + (t_end - t0) // 2
    R1, B1 = sub(R, (R["ts"] >= t0) & (R["ts"] < t_mid)), sub(B, (B["ts"] >= t0) & (B["ts"] < t_mid))
    h0 = t0 // HOUR
    Bw = sub(B, (B["ts"] >= t0) & (B["ts"] < t_end))
    H = int((t_end - t0) // HOUR) + 1
    cnt = np.zeros((H, 80, 3))
    np.add.at(cnt, (Bw["ts"] // HOUR - h0, Bw["item"].astype(int), Bw["pos"].astype(int) - 1), 1.0)
    tot = cnt.sum(1, keepdims=True)
    pi_h = np.divide(cnt, tot, out=np.zeros_like(cnt), where=tot > 0)
    # before-period cells: A needs V(W1, BTS) from Random logs; B needs V(W1, Random) from BTS logs
    wA_b = pi_h[R1["ts"] // HOUR - h0, R1["item"].astype(int), R1["pos"].astype(int) - 1] / R1["ps"]
    wB_b = (1.0 / 80) / B1["ps"]
    rows = []
    for dname, case, wb, rb in (("A_deploy_BTS", "halves · A deploy BTS", wA_b, R1["click"].astype(float)),
                                ("B_rollback_to_Random", "halves · B roll back", wB_b, B1["click"].astype(float))):
        rr = o["a3_halves"][dname]
        dr = rr["DR"]
        pe, pe_se = dr["policy_effect_after"], dr["se"]
        pb = 2 * dr["shapley_policy"] - pe
        pb_se = float(np.sqrt(max(dr["interaction_se"] ** 2 - pe_se ** 2, 0.0)))
        iv = lambda p, s: Interval(method="from obd_slice.json", level=0.95, point=p, lo=p - Z * s, hi=p + Z * s)
        sh = ShapleyDecomposition(naive=rr["naive"], policy=iv(dr["shapley_policy"], dr["shapley_policy_se"]), env=dr["shapley_env"],
                                  interaction=iv(dr["interaction"], dr["interaction_se"]), effect_after=iv(pe, pe_se), effect_before=iv(pb, pb_se))
        after_diag = {k: g[case][k] for k in ("ess_frac", "ess_r", "z_mean_w", "max_w", "n")}
        v = verdict(sh, {AFTER: after_diag, BEFORE: diagnostics(wb, rb)}, rule, scale=1000.0, unit=" per 1,000")
        rows.append((f"OBD halves · {dname}", v, f"truth (concurrent arms): after-period effect {1000 * rr['truth']:+.2f}, Shapley policy {1000 * rr['shapley_truth']['policy']:+.2f} per 1,000"))
    return rows


def main():
    rule = load_rule()
    L = ["# Demo verdicts (what the product prints)", "",
         "Reproduce: `nice -n 10 .venv/bin/python eval/demo_verdicts.py`. Simulator rows are SYNTHETIC (seed 0); OBD rows are REAL, with the gate applied POST HOC.", "",
         "| case | decision | what the tool says | ground truth (not seen by the tool) |", "|---|---|---|---|"]
    for name, v, truth in sim_cases(rule) + obd_cases(rule):
        L.append(f"| {name} | **{v.decision}** | {v.headline} | {truth} |")
    (ROOT / "eval" / "results" / "demo_verdicts.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
