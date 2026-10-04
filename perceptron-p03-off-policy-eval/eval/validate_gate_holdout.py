"""Held-out validation of the FROZEN overlap gate (eval/gate_rule.json + fixed guards) on simulator worlds and settings it
never saw. Pre-registered in eval/preregistration_gate_holdout.md before the first run. SYNTHETIC data.

Reproduce: cd perceptron-p03-off-policy-eval && nice -n 10 .venv/bin/python eval/validate_gate_holdout.py
Writes eval/results/gate_holdout{.md,.json,_runs.csv}.
"""
from __future__ import annotations

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
from components.report.gate import decide, diagnostics, load_rule  # noqa: E402
from components.simulator.sim import World, ground_truth, simulate  # noqa: E402

EFFECTS = {"positive": (0.7, 0.3), "near_null": (0.45, 0.40), "harmful": (0.3, 0.8)}
CONFIGS = {}
for ws, eff, eps, temp, off, n, K in itertools.product((101, 202), EFFECTS, (0.1, 0.02), (1.0, 4.0), (0.0, -4.0), (5000, 20000), (10, 40)):
    newq, oldq = EFFECTS[eff]
    CONFIGS[f"w{ws}_{eff}_eps{eps}_T{temp}_off{off}_n{n}_K{K}"] = (eff, dict(
        world_seed=ws, n_before=n, n_after=n, n_actions=K, response_drift=-0.5, new_policy_quality=newq,
        old_policy_quality=oldq, epsilon=eps, temperature=temp, reward_offset=off))
SEEDS = 8


def run_one(args):
    name, seed, truth, rule = args
    eff, kw = CONFIGS[name]
    sim = simulate(ScenarioConfig(name=name, seed=seed, **kw), truth)
    pi_old = ActionDist(probs=sim.world.policy(sim.after.X, "old"), policy="old")
    d = delta_vs_onpolicy("DR", sim.after, pi_old, crossfit_q(sim.after, seed=seed))
    ci = wald(d.influence)
    w = pi_old.probs[np.arange(len(sim.after.A)), sim.after.A] / sim.after.pscore
    dg = diagnostics(w, sim.after.R)
    answer, _ = decide(dg, rule)
    t = truth.policy_effect_after
    return dict(config=name, effect=eff, seed=seed, truth=t, est=d.delta, lo=ci.lo, hi=ci.hi, covered=ci.lo <= t <= ci.hi,
                confident_wrong_sign=bool((ci.lo > 0 > t) or (ci.hi < 0 < t)), answer=answer, **dg)


def summ(df):
    a = df[df.answer]
    return {"runs": int(len(df)), "answer_rate": float(df.answer.mean()),
            "coverage_answered": float(a.covered.mean()) if len(a) else None,
            "confident_wrong_answered": int(a.confident_wrong_sign.sum()), "answered": int(len(a)),
            "coverage_ungated": float(df.covered.mean()), "confident_wrong_ungated": int(df.confident_wrong_sign.sum()),
            "coverage_abstained": float(df[~df.answer].covered.mean()) if (~df.answer).any() else None}


def main():
    rule = load_rule()
    truths = {n: ground_truth(World(ScenarioConfig(name=n, **kw)), n_mc=200_000) for n, (_, kw) in CONFIGS.items()}
    jobs = [(n, s, truths[n], rule) for n in CONFIGS for s in range(SEEDS)]
    with ProcessPoolExecutor(6) as ex:
        df = pd.DataFrame(list(ex.map(run_one, jobs, chunksize=8)))
    res = ROOT / "eval" / "results"
    df.to_csv(res / "gate_holdout_runs.csv", index=False)
    out = {"pooled": summ(df), "by_effect": {e: summ(g) for e, g in df.groupby("effect")},
           "by_n": {int(n): summ(g) for n, g in df.groupby(df.config.str.extract(r"_n(\d+)_")[0].astype(int))},
           "by_K": {int(k): summ(g) for k, g in df.groupby(df.config.str.extract(r"_K(\d+)$")[0].astype(int))}}
    pre = out["pooled"]["coverage_answered"] is not None and out["pooled"]["coverage_answered"] >= 0.90 and all(
        v["coverage_answered"] is None or v["answered"] < 50 or v["coverage_answered"] >= 0.85 for v in out["by_effect"].values()) and (
        out["pooled"]["confident_wrong_answered"] / max(out["pooled"]["answered"], 1) <= out["pooled"]["confident_wrong_ungated"] / out["pooled"]["runs"])
    out["preregistered_criteria_met"] = bool(pre)
    (res / "gate_holdout.json").write_text(json.dumps(out, indent=1))
    P = out["pooled"]
    L = ["# Held-out validation of the frozen overlap gate (SIMULATOR; pre-registered)", "",
         "Pre-registration: [`../preregistration_gate_holdout.md`](../preregistration_gate_holdout.md). Reproduce: `nice -n 10 .venv/bin/python eval/validate_gate_holdout.py`.",
         f"{len(CONFIGS)} configurations × {SEEDS} seeds on world seeds 101 and 202 (calibration used 7). Effects positive, near-null and harmful; 10 or 40 actions; 5,000 or 20,000 rows per period. References are Monte-Carlo population values (200,000 draws).", "",
         f"**Pooled:** the gate answers {P['answer_rate']:.0%} of {P['runs']} runs. Coverage among answered: {P['coverage_answered']:.3f}; without the gate: {P['coverage_ungated']:.3f}. "
         f"Confident wrong-sign answers: {P['confident_wrong_answered']}/{P['answered']} answered vs {P['confident_wrong_ungated']}/{P['runs']} ungated. "
         f"Coverage on the abstained runs: {P['coverage_abstained']:.3f}. **Pre-registered criteria met: {'YES' if pre else 'NO'}.**", "",
         "| slice | runs | answer rate | coverage (answered) | coverage (ungated) | confident wrong (answered) | confident wrong (ungated) |", "|---|---|---|---|---|---|---|"]
    for grp, d in (("effect", out["by_effect"]), ("rows per period", out["by_n"]), ("actions", out["by_K"])):
        for k, v in d.items():
            ca = "—" if v["coverage_answered"] is None else f"{v['coverage_answered']:.3f}"
            L.append(f"| {grp} = {k} | {v['runs']} | {v['answer_rate']:.0%} | {ca} | {v['coverage_ungated']:.3f} | {v['confident_wrong_answered']}/{v['answered']} | {v['confident_wrong_ungated']}/{v['runs']} |")
    (res / "gate_holdout.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
