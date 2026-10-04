"""FROZEN evaluator for the C6 DeltaEstimator ratchet. The loop must never edit this file.

Prints one scalar: nRMSE = mean over scenarios of RMSE(delta_hat - truth) / |truth| (lower is better),
plus secondary metrics (Wald coverage, which must stay >= 0.90 so variance is not traded for bias silently).
Scenarios: a mini bank in the style of eval/run_sim_bank.py (SYNTHETIC; exact ground truth); `--holdout` swaps in
different world seeds that the loop never sees during iteration.
Reproduce: cd perceptron-p03-off-policy-eval && .venv/bin/python components/delta_estimator/autoresearch/eval.py [--holdout]
"""
from __future__ import annotations

import argparse
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from architecture.contracts.contracts import ActionDist, ScenarioConfig  # noqa: E402
from components.delta_estimator.delta import estimate_delta  # noqa: E402
from components.estimators.ope import crossfit_q  # noqa: E402
from components.intervals.ci import wald  # noqa: E402
from components.simulator.sim import World, ground_truth, simulate  # noqa: E402

MINI_BANK = {
    "drift_masks_gain": dict(response_drift=-1.0, mix_shift=0.5, new_policy_quality=0.7, old_policy_quality=0.3),
    "drift_fakes_gain": dict(response_drift=+1.0, new_policy_quality=0.3, old_policy_quality=0.8),
    "low_overlap": dict(response_drift=-0.3, epsilon=0.02, temperature=3.0, new_policy_quality=1.0, old_policy_quality=0.0),
    "small_effect": dict(response_drift=-0.2, new_policy_quality=0.45, old_policy_quality=0.4),
}
N, SEEDS = 5000, 12


def _one(args):
    name, world_seed, seed, truth = args
    cfg = ScenarioConfig(name=name, n_before=N, n_after=N, world_seed=world_seed, seed=seed, **MINI_BANK[name])
    sim = simulate(cfg, truth)
    pi_old = ActionDist(probs=sim.world.policy(sim.after.X, "old"), policy="old")
    d = estimate_delta(sim.after, pi_old, crossfit_q(sim.after, seed=seed))
    ci = wald(d.influence)
    return name, d.delta, ci.lo <= truth.policy_effect_after <= ci.hi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--holdout", action="store_true")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    world_seed = 1234 if a.holdout else 7
    truths = {s: ground_truth(World(ScenarioConfig(name=s, n_before=N, n_after=N, world_seed=world_seed, **kw)), n_mc=100_000)
              for s, kw in MINI_BANK.items()}
    jobs = [(s, world_seed, k, truths[s]) for s in MINI_BANK for k in range(SEEDS)]
    with ProcessPoolExecutor(a.workers) as ex:
        res = list(ex.map(_one, jobs))
    nrmse, cov = [], []
    for s in MINI_BANK:
        d = np.array([r[1] for r in res if r[0] == s])
        t = truths[s].policy_effect_after
        nrmse.append(np.sqrt(((d - t) ** 2).mean()) / abs(t))
        cov.append(np.mean([r[2] for r in res if r[0] == s]))
        print(f"  {s}: truth {t:+.4f} mean {d.mean():+.4f} nRMSE {nrmse[-1]:.4f} coverage {cov[-1]:.2f}")
    print(f"nRMSE={np.mean(nrmse):.5f} min_coverage={min(cov):.2f} split={'holdout' if a.holdout else 'dev'}")


if __name__ == "__main__":
    main()
