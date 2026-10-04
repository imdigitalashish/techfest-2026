"""Decomposer review experiments (SYNTHETIC simulator; exact ground truth) — Supervisor 13:05 fixes (a)-(d).

(d) drift sweep: where the naive before/after number is right and where it is wrong.
(b) 2x2 Shapley decomposition with OPE filling both unobserved cells, plus the interaction term (in every experiment).
(a) feedback knob: a policy-induced audience shift; the identified policy term is the DIRECT effect; we quantify the gap.
(c) misspecification: a reward term the linear-logistic model cannot fit; DM vs DR policy term; DM vs DR mix/drift split.
Reproduce: cd perceptron-p03-off-policy-eval && nice -n 10 .venv/bin/python eval/run_decomposer_review.py --seeds 20
Writes eval/results/decomposer_review{.md,.json,_runs.csv} and deliverables/figures/drift_sweep.png.
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from architecture.contracts.contracts import ActionDist, ScenarioConfig  # noqa: E402
from components.decomposer.decompose import decompose, shapley  # noqa: E402
from components.estimators.ope import crossfit_q, delta_vs_onpolicy  # noqa: E402
from components.simulator.sim import World, ground_truth, simulate  # noqa: E402

BASE = dict(n_before=10_000, n_after=10_000, new_policy_quality=0.7, old_policy_quality=0.3)
DRIFTS = [round(x, 2) for x in np.linspace(-1.5, 1.5, 13)]
EXPERIMENTS = {}
for dft in DRIFTS:
    EXPERIMENTS[f"drift{dft:+.2f}"] = ("drift", dict(BASE, response_drift=dft, mix_shift=0.0))
for fb in (0.0, 0.25, 0.5, 1.0):
    EXPERIMENTS[f"feedback{fb:.2f}"] = ("feedback", dict(BASE, response_drift=-1.0, mix_shift=0.0, feedback=fb))
for lam in (0.0, 1.0, 2.0):
    EXPERIMENTS[f"nonlin{lam:.1f}"] = ("misspec", dict(BASE, response_drift=-1.0, mix_shift=0.5, nonlinearity=lam))
for lam in (1.0, 2.0):
    EXPERIMENTS[f"nonlinmix{lam:.1f}"] = ("misspec", dict(BASE, response_drift=-1.0, mix_shift=0.5, nonlinearity=lam, nonlinear_axis="mix"))


def run_one(args):
    name, seed, truth = args
    cfg = ScenarioConfig(name=name, seed=seed, **EXPERIMENTS[name][1])
    sim = simulate(cfg, truth)
    w = sim.world
    pi_old_a = ActionDist(probs=w.policy(sim.after.X, "old"), policy="old")
    pi_old_b = ActionDist(probs=w.policy(sim.before.X, "old"), policy="old")
    pi_new_b = ActionDist(probs=w.policy(sim.before.X, "new"), policy="new")
    qa, qb = crossfit_q(sim.after, seed=seed), crossfit_q(sim.before, seed=seed)
    sh = shapley(sim.before, sim.after, pi_new_b, pi_old_a, "DR", q_before=qb, q_after=qa)
    dm_pol = delta_vs_onpolicy("DM", sim.after, pi_old_a, qa).delta
    dec_dm = decompose(sim.before, sim.after, pi_old_a, pi_old_b, "DR", q_after=qa, mix_method="DM")
    dec_dr = decompose(sim.before, sim.after, pi_old_a, pi_old_b, "DR", q_after=qa, mix_method="DR")
    return dict(exp=name, kind=EXPERIMENTS[name][0], seed=seed, naive=sh.naive,
                dr_after=sh.effect_after.point, dr_after_lo=sh.effect_after.lo, dr_after_hi=sh.effect_after.hi,
                dr_before=sh.effect_before.point, shap_pol=sh.policy.point, shap_pol_lo=sh.policy.lo, shap_pol_hi=sh.policy.hi,
                inter=sh.interaction.point, inter_lo=sh.interaction.lo, inter_hi=sh.interaction.hi, dm_after=dm_pol,
                mix_dm=dec_dm.mix_shift, drift_dm=dec_dm.response_drift, mix_dr=dec_dr.mix_shift, drift_dr=dec_dr.response_drift)


def agg(df, truths):
    out = {}
    for name, g in df.groupby("exp", sort=False):
        t = truths[name]
        te = t.policy_effect_after
        rmse = lambda x, y: float(np.sqrt(((x - y) ** 2).mean()))
        out[name] = {
            "kind": g.kind.iloc[0], "seeds": int(len(g)),
            "truth": {"effect_after": te, "effect_before": t.policy_effect_before, "shapley_policy": t.shapley_policy,
                      "interaction": t.interaction, "naive_expected": t.naive_expected, "total_effect": t.total_effect,
                      "feedback_population_effect": t.feedback_population_effect, "mix": t.mix_shift, "drift": t.response_drift},
            "naive_mean": float(g.naive.mean()), "naive_sign_ok": float(np.mean(np.sign(g.naive) == np.sign(te))),
            "naive_rmse": rmse(g.naive, te), "dr_mean": float(g.dr_after.mean()), "dr_rmse": rmse(g.dr_after, te),
            "dr_sign_ok": float(np.mean(np.sign(g.dr_after) == np.sign(te))),
            "dr_cover": float(np.mean((g.dr_after_lo <= te) & (te <= g.dr_after_hi))),
            "dr_vs_total_bias": float(g.dr_after.mean() - t.total_effect),
            "dm_mean": float(g.dm_after.mean()), "dm_bias": float(g.dm_after.mean() - te),
            "shap_mean": float(g.shap_pol.mean()), "shap_rmse": rmse(g.shap_pol, t.shapley_policy),
            "shap_cover": float(np.mean((g.shap_pol_lo <= t.shapley_policy) & (t.shapley_policy <= g.shap_pol_hi))),
            "inter_mean": float(g.inter.mean()), "inter_cover": float(np.mean((g.inter_lo <= t.interaction) & (t.interaction <= g.inter_hi))),
            "mix_dm_bias": float(g.mix_dm.mean() - t.mix_shift), "mix_dr_bias": float(g.mix_dr.mean() - t.mix_shift),
            "mix_dm_rmse": rmse(g.mix_dm, t.mix_shift), "mix_dr_rmse": rmse(g.mix_dr, t.mix_shift),
        }
    return out


def report(a, seeds):
    L = ["# Decomposer review — results (SYNTHETIC simulator, exact ground truth)", "",
         f"Reproduce: `nice -n 10 .venv/bin/python eval/run_decomposer_review.py --seeds {seeds}` (from `perceptron-p03-off-policy-eval/`). "
         "10,000 logged rounds per period; new-policy quality 0.7, old 0.3; DR = doubly robust with a cross-fitted logistic reward model; ± = 95%.", "",
         "## (d) Drift sweep — where naive is right and where it is wrong (mix shift 0)", "",
         "| response drift (logit) | true effect (after) | naive mean | naive sign correct | naive RMSE | DR mean | DR RMSE | DR coverage | Shapley policy est vs truth | interaction est vs truth |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for k, v in a.items():
        if v["kind"] != "drift":
            continue
        t = v["truth"]
        L.append(f"| {k[5:]} | {t['effect_after']:+.4f} | {v['naive_mean']:+.4f} | {v['naive_sign_ok']:.0%} | {v['naive_rmse']:.4f} | {v['dr_mean']:+.4f} | {v['dr_rmse']:.4f} | {v['dr_cover']:.2f} | "
                 f"{v['shap_mean']:+.4f} vs {t['shapley_policy']:+.4f} | {v['inter_mean']:+.4f} vs {t['interaction']:+.4f} |")
    dr = [v for v in a.values() if v["kind"] == "drift"]
    right = [k[5:] for k, v in a.items() if v["kind"] == "drift" and v["naive_sign_ok"] == 1.0]
    wrong = [k[5:] for k, v in a.items() if v["kind"] == "drift" and v["naive_sign_ok"] == 0.0]
    L += ["", f"Naive has the right sign in every seed at drifts {', '.join(right)}; the wrong sign in every seed at {', '.join(wrong) or 'none'}. "
          f"DR's RMSE stays in {min(v['dr_rmse'] for v in dr):.4f}–{max(v['dr_rmse'] for v in dr):.4f} across the sweep; "
          f"naive's ranges {min(v['naive_rmse'] for v in dr):.4f}–{max(v['naive_rmse'] for v in dr):.4f}.", "",
          "## (a) Feedback — the policy changes who shows up (drift −1.0)", "",
          "| feedback | direct effect (truth) | total effect (truth) | population effect (truth) | DR mean | DR − direct | DR − total | DR coverage of direct |", "|---|---|---|---|---|---|---|---|"]
    for k, v in a.items():
        if v["kind"] != "feedback":
            continue
        t = v["truth"]
        L.append(f"| {k[8:]} | {t['effect_after']:+.4f} | {t['total_effect']:+.4f} | {t['feedback_population_effect']:+.4f} | {v['dr_mean']:+.4f} | "
                 f"{v['dr_mean'] - t['effect_after']:+.4f} | {v['dr_vs_total_bias']:+.4f} | {v['dr_cover']:.2f} |")
    L += ["", "The logs identify the direct effect. The audience the policy attracted (population effect) is booked as mix shift, and the total effect is not identified from the after-period logs alone.", "",
          "## (c) Misspecification — reward term the logistic model cannot fit (drift −1.0, mix 0.5)", "",
          "| nonlinearity | true effect | DR policy term (bias) | DM policy term (bias) | true mix | DM-mix bias (RMSE) | DR-mix bias (RMSE) | DR coverage |", "|---|---|---|---|---|---|---|---|"]
    for k, v in a.items():
        if v["kind"] != "misspec":
            continue
        t = v["truth"]
        L.append(f"| {k[6:].replace('mix', 'along mix axis, ')} | {t['effect_after']:+.4f} | {v['dr_mean']:+.4f} ({v['dr_mean'] - t['effect_after']:+.4f}) | {v['dm_mean']:+.4f} ({v['dm_bias']:+.4f}) | "
                 f"{t['mix']:+.4f} | {v['mix_dm_bias']:+.4f} ({v['mix_dm_rmse']:.4f}) | {v['mix_dr_bias']:+.4f} ({v['mix_dr_rmse']:.4f}) | {v['dr_cover']:.2f} |")
    L += ["", "## (b) Shapley coverage summary", "",
          "Mean 95% coverage across all experiments: Shapley policy "
          f"{np.mean([v['shap_cover'] for v in a.values()]):.2f}; interaction {np.mean([v['inter_cover'] for v in a.values()]):.2f}; "
          f"after-effect (v0 term) {np.mean([v['dr_cover'] for v in a.values()]):.2f}.", ""]
    return "\n".join(L)


def plot(a):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = [(float(k[5:]), v) for k, v in a.items() if v["kind"] == "drift"]
    x = [r[0] for r in rows]
    fig, ax = plt.subplots(figsize=(7.5, 4))
    ax.plot(x, [r[1]["truth"]["effect_after"] for r in rows], "k--", lw=2, label="truth: what the switch did")
    ax.plot(x, [r[1]["dr_mean"] for r in rows], "o-", color="#2b8a3e", label="our estimate (DR, mean of seeds)")
    ax.plot(x, [r[1]["naive_mean"] for r in rows], "s-", color="#495057", label="dashboard: naive after − before")
    ax.axhline(0, color="grey", lw=0.8)
    ax.set_xlabel("seasonal drift between the periods (logit shift)")
    ax.set_ylabel("change in reward rate")
    ax.legend(fontsize=8)
    ax.set_title("Naive is right only when the season stands still", fontsize=10)
    fig.text(0.01, 0.01, "SYNTHETIC simulator; eval/run_decomposer_review.py", fontsize=7)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    out = ROOT / "deliverables" / "figures"
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / "drift_sweep.png", dpi=130)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    truths = {n: ground_truth(World(ScenarioConfig(name=n, **kw)), n_mc=200_000) for n, (_, kw) in EXPERIMENTS.items()}
    jobs = [(n, s, truths[n]) for n in EXPERIMENTS for s in range(a.seeds)]
    with ProcessPoolExecutor(a.workers) as ex:
        df = pd.DataFrame(list(ex.map(run_one, jobs, chunksize=4)))
    res = ROOT / "eval" / "results"
    df.to_csv(res / "decomposer_review_runs.csv", index=False)
    ag = agg(df, truths)
    (res / "decomposer_review.json").write_text(json.dumps(ag, indent=1))
    md = report(ag, a.seeds)
    (res / "decomposer_review.md").write_text(md + "\n")
    plot(ag)
    print(md)


if __name__ == "__main__":
    main()
