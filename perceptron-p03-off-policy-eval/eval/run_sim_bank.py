"""C12 EvalHarness (v0): frozen scenario bank x seeds against exact ground truth (SYNTHETIC simulator, C11).

Reproduce:  cd perceptron-p03-off-policy-eval && .venv/bin/python eval/run_sim_bank.py --seeds 60
Writes eval/results/sim_bank_runs.csv and eval/results/sim_bank_summary.md.
"""
from __future__ import annotations

import argparse
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from architecture.contracts.contracts import ActionDist, ScenarioConfig  # noqa: E402
from components.decomposer.decompose import decompose  # noqa: E402
from components.estimators.ope import crossfit_q, delta_vs_onpolicy  # noqa: E402
from components.intervals.ci import wald  # noqa: E402
from components.sensitivity.msm import delta_curve  # noqa: E402
from components.simulator.sim import World, ground_truth, simulate  # noqa: E402

# FROZEN scenario bank v0 (do not edit; add a new version instead). All data SYNTHETIC.
BANK = {
    "S1_drift_masks_gain": dict(response_drift=-1.0, mix_shift=0.5, new_policy_quality=0.7, old_policy_quality=0.3),
    "S2_drift_fakes_gain": dict(response_drift=+1.0, mix_shift=0.0, new_policy_quality=0.3, old_policy_quality=0.8),
    "S3_stationary_control": dict(response_drift=0.0, mix_shift=0.0, new_policy_quality=1.0, old_policy_quality=0.3),
    "S4_hidden_override": dict(response_drift=-0.3, hidden_confounding=1.0, new_policy_quality=0.6, old_policy_quality=0.5),
    "S5_low_overlap": dict(response_drift=-0.3, epsilon=0.02, temperature=3.0, new_policy_quality=1.0, old_policy_quality=0.0),
}
COMMON = dict(n_before=10_000, n_after=10_000)
ESTIMATORS = ["IPW", "SNIPW", "DM", "DR", "SwitchDR"]
GAMMAS = [1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 7.0, 10.0]


def run_one(args):
    name, seed, truth, do_msm = args
    cfg = ScenarioConfig(name=name, seed=seed, **COMMON, **BANK[name])
    sim = simulate(cfg, truth)
    w: World = sim.world
    pi_old_after = ActionDist(probs=w.policy(sim.after.X, "old"), policy="old")
    pi_old_before = ActionDist(probs=w.policy(sim.before.X, "old"), policy="old")
    q_after = crossfit_q(sim.after, seed=seed)
    t = sim.truth
    rows = []
    naive = float(sim.after.R.mean() - sim.before.R.mean())
    for est in ESTIMATORS:
        d = delta_vs_onpolicy(est, sim.after, pi_old_after, q_after)
        ci = wald(d.influence)
        rows.append(dict(scenario=name, seed=seed, estimator=est, truth=t.policy_effect_after, naive=naive,
                         delta=d.delta, lo=ci.lo, hi=ci.hi, covered=ci.lo <= t.policy_effect_after <= ci.hi,
                         ess=d.diagnostics["ess"], max_w=d.diagnostics["max_weight"]))
    dec = decompose(sim.before, sim.after, pi_old_after, pi_old_before, "DR", q_after=q_after)
    rows.append(dict(scenario=name, seed=seed, estimator="DECOMP", truth=t.policy_effect_after, naive=naive,
                     delta=dec.policy_effect.point, lo=dec.policy_effect.lo, hi=dec.policy_effect.hi,
                     covered=dec.policy_effect.lo <= t.policy_effect_after <= dec.policy_effect.hi,
                     mix_hat=dec.mix_shift, mix_true=t.mix_shift, drift_hat=dec.response_drift, drift_true=t.response_drift))
    if do_msm:
        c = pi_old_after.probs[np.arange(len(sim.after.A)), sim.after.A]
        curve = delta_curve(c, sim.after.pscore, sim.after.R, GAMMAS, B=100, seed=seed)
        g_idx = next((i for i, g in enumerate(GAMMAS) if g >= t.gamma_true), len(GAMMAS) - 1)
        rows.append(dict(scenario=name, seed=seed, estimator="MSM_HAJEK", truth=t.policy_effect_after, naive=naive,
                         delta=(curve.lo[0] + curve.hi[0]) / 2, lo=curve.lo[0], hi=curve.hi[0],
                         covered=curve.lo[g_idx] <= t.policy_effect_after <= curve.hi[g_idx],
                         gamma_star=curve.gamma_star, gamma_true=t.gamma_true, msm_lo=curve.lo[g_idx], msm_hi=curve.hi[g_idx]))
    return rows


def summarise(df: pd.DataFrame, truths: dict) -> str:
    out = ["# Simulator bank v0 — results (SYNTHETIC data, exact ground truth)", "",
           "Reproduce: `.venv/bin/python eval/run_sim_bank.py --seeds %d` (from `perceptron-p03-off-policy-eval/`)." % df.seed.nunique(), "",
           "Policy effect = V_after(new, as deployed) − V_after(old): what the switch did, on the same after-period traffic.", ""]
    for s, t in truths.items():
        out.append(f"## {s}")
        out.append(f"Truth: V_before(old)={t.v_before_old:.4f} · V_after(new)={t.v_after_new:.4f} · V_after(old)={t.v_after_old:.4f} · "
                   f"**policy effect={t.policy_effect_after:+.4f}** · expected naive={t.naive_expected:+.4f} · mix={t.mix_shift:+.4f} · drift={t.response_drift:+.4f} · Γ_true={t.gamma_true:.2f}")
        d = df[df.scenario == s]
        nv = d[d.estimator == "DR"].naive
        out.append(f"Naive before/after: mean {nv.mean():+.4f} (sd {nv.std():.4f}); sign matches truth in {np.mean(np.sign(nv) == np.sign(t.policy_effect_after)):.0%} of seeds; RMSE vs policy effect {np.sqrt(((nv - t.policy_effect_after) ** 2).mean()):.4f}")
        out.append("")
        out.append("| estimator | mean Δ̂ | bias | RMSE | 95% Wald coverage | mean CI width | sign correct | mean ESS |")
        out.append("|---|---|---|---|---|---|---|---|")
        for e in ESTIMATORS:
            x = d[d.estimator == e]
            out.append(f"| {e} | {x.delta.mean():+.4f} | {x.delta.mean() - t.policy_effect_after:+.4f} | {np.sqrt(((x.delta - t.policy_effect_after) ** 2).mean()):.4f} | "
                       f"{x.covered.mean():.2f} | {(x.hi - x.lo).mean():.4f} | {np.mean(np.sign(x.delta) == np.sign(t.policy_effect_after)):.0%} | {x.ess.mean():.0f} |")
        dc = d[d.estimator == "DECOMP"]
        out.append("")
        out.append(f"Decomposition (DR policy term + DM mix/drift split): mix̂ {dc.mix_hat.mean():+.4f} vs true {t.mix_shift:+.4f}; drift̂ {dc.drift_hat.mean():+.4f} vs true {t.response_drift:+.4f}")
        ms = d[d.estimator == "MSM_HAJEK"]
        if len(ms):
            gs = ms.gamma_star.dropna()
            out.append(f"MSM (Hajek, joint bootstrap B=100, {len(ms)} seeds): truth inside bounds at Γ ≥ Γ_true in {ms.covered.mean():.0%}; "
                       f"Γ* (interval first contains 0): median {gs.median() if len(gs) else float('nan'):.2f} ({len(gs)}/{len(ms)} seeds reach 0 within Γ ≤ {GAMMAS[-1]})")
        out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=60)
    ap.add_argument("--msm_seeds", type=int, default=10)
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    truths = {s: ground_truth(World(ScenarioConfig(name=s, **COMMON, **kw)), n_mc=200_000) for s, kw in BANK.items()}
    jobs = [(s, k, truths[s], s == "S4_hidden_override" and k < a.msm_seeds) for s in BANK for k in range(a.seeds)]
    with ProcessPoolExecutor(a.workers) as ex:
        rows = [r for rs in ex.map(run_one, jobs) for r in rs]
    df = pd.DataFrame(rows)
    res = ROOT / "eval" / "results"
    res.mkdir(parents=True, exist_ok=True)
    df.to_csv(res / "sim_bank_runs.csv", index=False)
    md = summarise(df, truths)
    (res / "sim_bank_summary.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
