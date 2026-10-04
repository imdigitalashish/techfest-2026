"""Coverage test for moderated block estimates (spike 2) + pre-registered allocation comparison. SYNTHETIC data.

Pre-registration: eval/preregistration/2026-10-04-coverage.md (committed before the held-out run).
Usage:
  python3 eval/coverage_test.py --seeds 101-130 --out eval/results/coverage_heldout.json            # primary
  python3 eval/coverage_test.py --seeds 101-130 --subject numeracy --out ...                        # secondary
  python3 eval/coverage_test.py --seeds 101-130 --budget 0.05 --out ...                             # secondary
  python3 eval/coverage_test.py --seeds 101-130 --need-corr 1.0 --out ...                           # stress scenario
Development seeds used while building the method: 1-30. Held-out seeds: 101-130.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from components.allocation.core import below_goal_children_reached, target_schools
from components.trust_audit.assurance import Design, run_assurance
from components.trust_audit.core import forensic_flags, retest, select_audit
from eval.sim.calibration import ASER2024_GOVT_STD3
from eval.sim.world import make_world

K_STRATA, R_BOOT, BIAS_MODEL, CHILDREN_PER_SCHOOL, DOUBLE_CHECK = 4, 200, "mean", 12, 0.2


def parse_seeds(s: str) -> list[int]:
    out = []
    for part in s.split(","):
        if "-" in part:
            a, b = part.split("-"); out += list(range(int(a), int(b) + 1))
        elif part:
            out.append(int(part))
    return out


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return float(c - h), float(c + h)


def run_seed(seed: int, subject: str, budget: float, need_corr: float) -> tuple[pd.DataFrame, dict]:
    w = make_world(seed, {**ASER2024_GOVT_STD3, "inflation_need_corr": need_corr})
    pub = w.public_view()
    risk = forensic_flags(pub.teacher_reports, pub.schools, pub.item_responses, pub.item_bank, subject=subject)
    b = max(1, round(budget * len(pub.schools)))
    sel = select_audit(pub.schools, risk, b, "risk_pps", seed=seed + 17)
    aud = retest(w, sel, CHILDREN_PER_SCHOOL, subject=subject, seed=seed + 31, double_check_frac=DOUBLE_CHECK)
    ctx, fit, iv = run_assurance(pub, risk, sel, aud, Design(budget=b, children_per_school=CHILDREN_PER_SCHOOL, double_check_frac=DOUBLE_CHECK),
                                 subject=subject, k_strata=K_STRATA, R=R_BOOT, seed=seed + 53, bias_model=BIAS_MODEL)
    goal = "read_goal" if subject == "language" else "math_goal"
    t = w.children.groupby("udise_code")[goal].sum().rename("k").to_frame().join(w.schools.set_index("udise_code")[["block_lgd", "grade3_enrolment"]])
    truth = (t.groupby("block_lgd").k.sum() / t.groupby("block_lgd").grade3_enrolment.sum()).rename("true")
    raw = risk.assign(x=risk.reported_pct_meeting_goal * risk.grade3_enrolment).groupby("block_lgd").apply(
        lambda g: g.x.sum() / g.grade3_enrolment.sum(), include_groups=False).rename("raw")
    iv = iv.join(truth, on="block_lgd").join(raw, on="block_lgd")
    iv["covered"] = (iv.lo <= iv["true"]) & (iv["true"] <= iv.hi)
    iv["seed"] = seed
    # pre-registered allocation comparison (effect-free): below-goal children in the top-10 % targeted schools
    R = max(1, round(0.10 * len(pub.schools)))
    codes = ctx.schools.udise_code
    raw_p = pd.Series(ctx.r, index=codes); mod_p = pd.Series(fit.school_est, index=codes)
    true_p = w.children.groupby("udise_code")[goal].mean()
    alloc = {"seed": seed,
             "raw": below_goal_children_reached(w, target_schools(pub.schools, raw_p, R), subject),
             "moderated": below_goal_children_reached(w, target_schools(pub.schools, mod_p, R), subject),
             "oracle": below_goal_children_reached(w, target_schools(pub.schools, true_p, R), subject),
             "eps_hat": fit.eps, "tau2_hat": fit.extras["tau2"], "n_audited": fit.n_audited}
    return iv, alloc


def summarise(blocks: pd.DataFrame, alloc: pd.DataFrame) -> dict:
    out = {}
    for method in ["fh", "direct"]:
        g = blocks[blocks.method == method]
        k, n = int(g.covered.sum()), len(g)
        out[method] = {"coverage90": k / n, "coverage_wilson95": wilson(k, n), "n_blocks": n,
                       "mae_pp": float((g.estimate - g["true"]).abs().mean() * 100), "raw_mae_pp": float((g.raw - g["true"]).abs().mean() * 100),
                       "mean_half_width_pp": float(((g.hi - g.lo) / 2).mean() * 100), "mean_error_pp": float((g.estimate - g["true"]).mean() * 100)}
    d = alloc["moderated"] - alloc["raw"]
    se = float(d.std(ddof=1) / np.sqrt(len(d))) if len(d) > 1 else float("nan")
    out["allocation"] = {"raw_mean": float(alloc.raw.mean()), "moderated_mean": float(alloc.moderated.mean()), "oracle_mean": float(alloc.oracle.mean()),
                         "diff_moderated_minus_raw_mean": float(d.mean()), "diff_ci95": [float(d.mean() - 1.96 * se), float(d.mean() + 1.96 * se)],
                         "gain_shown": bool(d.mean() - 1.96 * se > 0), "n_worlds": int(len(alloc))}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="101-130"); ap.add_argument("--subject", default="language")
    ap.add_argument("--budget", type=float, default=0.10); ap.add_argument("--need-corr", type=float, default=0.0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    seeds = parse_seeds(a.seeds); t0 = time.time()
    rows, allocs = [], []
    for s in seeds:
        iv, al = run_seed(s, a.subject, a.budget, a.need_corr); rows.append(iv); allocs.append(al)
    blocks = pd.concat(rows, ignore_index=True); alloc = pd.DataFrame(allocs)
    summ = summarise(blocks, alloc)
    res = {"synthetic": True, "seeds": a.seeds, "subject": a.subject, "budget_frac": a.budget, "inflation_need_corr": a.need_corr,
           "method": {"k_strata": K_STRATA, "bootstrap_R": R_BOOT, "bias_model": BIAS_MODEL, "children_per_school": CHILDREN_PER_SCHOOL,
                      "double_check_frac": DOUBLE_CHECK, "design": "risk_pps"},
           "primary": {"metric": "coverage of nominal 90% intervals (method fh), true block share meeting the goal", "threshold": 0.85,
                       "pass": bool(summ["fh"]["coverage90"] >= 0.85)},
           "secondary_mae_pass": bool(summ["fh"]["mae_pp"] < summ["fh"]["raw_mae_pp"]),
           "summary": summ, "runtime_s": round(time.time() - t0, 1),
           "command": "python3 eval/coverage_test.py " + " ".join(sys.argv[1:])}
    print(json.dumps({k: res[k] for k in ["primary", "secondary_mae_pass"]}), json.dumps(summ["fh"]), json.dumps(summ["allocation"]))
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(res, indent=2) + "\n")
        blocks.to_csv(Path(a.out).with_suffix(".blocks.csv"), index=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
