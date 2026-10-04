"""Calibrate the overlap gate on the SIMULATOR ONLY (no OBD data is read here).

Calibration bank: overlap (epsilon x temperature, old scorer random), reward sparsity (reward_offset) and Monte-Carlo
noise on logged propensities (as in OBD's BTS logs), x seeds. For each run: DR policy effect, its 95% Wald CI, truth,
and the gate diagnostics. Threshold grid search: maximise the answer rate subject to (pooled coverage among answered
runs >= 0.93) and (every config with >= 5 answered runs has coverage >= 0.85); tau_z is fixed a priori at 3.
Reproduce: cd perceptron-p03-off-policy-eval && nice -n 10 .venv/bin/python eval/calibrate_gate.py --seeds 20
Writes eval/gate_rule.json, eval/results/gate_calibration{.md,_runs.csv}.
"""
from __future__ import annotations

import argparse
import datetime as dt
import itertools
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from architecture.contracts.contracts import ActionDist, ScenarioConfig  # noqa: E402
from components.estimators.ope import crossfit_q, delta_vs_onpolicy  # noqa: E402
from components.intervals.ci import wald  # noqa: E402
from components.report.gate import diagnostics  # noqa: E402
from components.simulator.sim import World, ground_truth, simulate  # noqa: E402

CONFIGS = {}
for eps, temp, off, mc in itertools.product((0.1, 0.02, 0.005), (1.0, 4.0), (0.0, -3.0, -5.0), (0, 100_000)):
    CONFIGS[f"eps{eps}_T{temp}_off{off}_mc{mc}"] = dict(
        n_before=10_000, n_after=10_000, response_drift=-0.5, new_policy_quality=1.0, old_policy_quality=0.0,
        epsilon=eps, temperature=temp, reward_offset=off, pscore_noise_sims=mc)
TAU_ESS = [0.0, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1]
TAU_R = [0, 5, 10, 20, 50, 100, 200]
TAU_Z = 3.0


def run_one(args):
    name, seed, truth = args
    sim = simulate(ScenarioConfig(name=name, seed=seed, **CONFIGS[name]), truth)
    pi_old = ActionDist(probs=sim.world.policy(sim.after.X, "old"), policy="old")
    d = delta_vs_onpolicy("DR", sim.after, pi_old, crossfit_q(sim.after, seed=seed))
    ci = wald(d.influence)
    w = pi_old.probs[np.arange(len(sim.after.A)), sim.after.A] / sim.after.pscore
    t = truth.policy_effect_after
    return dict(config=name, seed=seed, truth=t, est=d.delta, lo=ci.lo, hi=ci.hi, covered=ci.lo <= t <= ci.hi,
                wrong_sign_confident=(np.sign(ci.lo) == np.sign(ci.hi)) and (np.sign(ci.lo) != np.sign(t)),
                ctr=float(sim.after.R.mean()), **diagnostics(w, sim.after.R))


def evaluate(df, te, tr):
    ans = (df.ess_frac >= te) & (df.ess_r >= tr) & (df.z_mean_w.abs() <= TAU_Z)
    a = df[ans]
    per = a.groupby("config").covered.agg(["mean", "size"])
    worst = per[per["size"] >= 5]["mean"].min() if (per["size"] >= 5).any() else np.nan
    return dict(tau_ess=te, tau_r=tr, answer_rate=float(ans.mean()), pooled_cov=float(a.covered.mean()) if len(a) else np.nan,
                worst_cfg_cov=float(worst), confident_wrong=int(a.wrong_sign_confident.sum()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    truths = {n: ground_truth(World(ScenarioConfig(name=n, **kw)), n_mc=200_000) for n, kw in CONFIGS.items()}
    with ProcessPoolExecutor(a.workers) as ex:
        df = pd.DataFrame(list(ex.map(run_one, [(n, s, truths[n]) for n in CONFIGS for s in range(a.seeds)], chunksize=4)))
    res = ROOT / "eval" / "results"
    df.to_csv(res / "gate_calibration_runs.csv", index=False)
    grid = pd.DataFrame([evaluate(df, te, tr) for te in TAU_ESS for tr in TAU_R])
    ok = grid[(grid.pooled_cov >= 0.93) & ((grid.worst_cfg_cov >= 0.85) | grid.worst_cfg_cov.isna())]
    best = ok.sort_values(["answer_rate", "tau_ess", "tau_r"], ascending=[False, True, True]).iloc[0]
    ungated = evaluate(df, 0.0, 0)
    rule = {"tau_ess": float(best.tau_ess), "tau_r": float(best.tau_r), "tau_z": TAU_Z,
            "calibrated_at": dt.datetime.now(dt.timezone(dt.timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d %H:%M:%S IST"),
            "calibration": "simulator only (eval/calibrate_gate.py); never fitted to OBD",
            "answer_rate": float(best.answer_rate), "pooled_coverage_answered": float(best.pooled_cov),
            "confident_wrong_answered": int(best.confident_wrong), "ungated": ungated}
    (ROOT / "eval" / "gate_rule.json").write_text(json.dumps(rule, indent=1))
    per_cfg = df.groupby("config").agg(ess_frac=("ess_frac", "median"), ess_r=("ess_r", "median"), z=("z_mean_w", "median"),
                                       ctr=("ctr", "mean"), coverage=("covered", "mean"), conf_wrong=("wrong_sign_confident", "sum"))
    L = ["# Overlap-gate calibration (SIMULATOR ONLY)", "",
         f"Reproduce: `nice -n 10 .venv/bin/python eval/calibrate_gate.py --seeds {a.seeds}`. {len(CONFIGS)} configs × {a.seeds} seeds; DR policy effect with a 95% Wald CI.", "",
         f"**Chosen rule:** abstain if ESS/n < {rule['tau_ess']} or effective rewards < {rule['tau_r']:.0f} or |mean-weight z| > {TAU_Z}. "
         f"Answer rate {rule['answer_rate']:.0%}; coverage among answered {rule['pooled_coverage_answered']:.2f}; confident wrong-sign answers among answered: {rule['confident_wrong_answered']}.",
         f"Without the gate: coverage {ungated['pooled_cov']:.2f}, worst config {ungated['worst_cfg_cov']:.2f}, confident wrong-sign answers {ungated['confident_wrong']} of {len(df)}.", "",
         "| config | median ESS/n | median effective rewards | median mean-weight z | mean reward rate | DR coverage | confident wrong-sign |", "|---|---|---|---|---|---|---|"]
    L += [f"| {c} | {r.ess_frac:.4f} | {r.ess_r:.0f} | {r.z:+.1f} | {r.ctr:.3f} | {r.coverage:.2f} | {int(r.conf_wrong)} |" for c, r in per_cfg.iterrows()]
    L += ["", "Grid (feasible rules first):", "", "| tau_ess | tau_r | answer rate | pooled coverage | worst config coverage | confident wrong |", "|---|---|---|---|---|---|"]
    L += [f"| {r.tau_ess} | {r.tau_r:.0f} | {r.answer_rate:.2f} | {r.pooled_cov:.3f} | {r.worst_cfg_cov:.2f} | {r.confident_wrong} |" for _, r in ok.head(8).iterrows()]
    (res / "gate_calibration.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:8]))


if __name__ == "__main__":
    main()
