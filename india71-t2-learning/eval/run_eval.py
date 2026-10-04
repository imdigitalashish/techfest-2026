"""End-to-end SYNTHETIC demo + the single source of headline numbers.

Usage (from india71-t2-learning/):  nice -n 10 python3 eval/run_eval.py
Writes eval/results/headline.json, eval/results/summary.md, deliverables/demo/block_dashboard.html (+ JSON) and
deliverables/demo/teacher_plan_*.txt. Headline numbers come from:
  - pre-registered held-out coverage runs (eval/results/coverage_heldout*.json, eval/preregistration/2026-10-04-coverage.md)
  - exploratory separation analysis on the same held-out outputs (labelled exploratory)
  - risk-score detection AUC on held-out seeds 101-130
  - C4 diagnostics evaluator (components/diagnostics/evaluate.py, seeds 101-105)
  - C7 teacher plan for one synthetic class; C12 policy suite.
All child-level data are SYNTHETIC (eval/sim/world.py), calibrated to ASER 2024 (eval/sim/calibration.py).
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from components.dashboard import build_dashboard
from components.diagnostics.engine import adaptive_test
from components.diagnostics.evaluate import evaluate_seeds
from components.diagnostics.cutpoints import load as load_cutpoints
from components.teacher_view.planner import make_plan, render_ivr_script, sms_segments
from components.trust_audit.assurance import Design, run_assurance
from components.trust_audit.core import detection_auc, forensic_flags, retest, select_audit
from eval.sim.calibration import ASER2024_GOVT_STD3
from eval.sim.world import make_world

RES = ROOT / "eval" / "results"
DEMO = ROOT / "deliverables" / "demo"
HELDOUT = list(range(101, 131))


def coverage_results() -> dict:
    out = {}
    for key, f in [("language_b10", "coverage_heldout"), ("numeracy_b10", "coverage_heldout_numeracy"), ("language_b05", "coverage_heldout_b05"),
                   ("language_b20", "coverage_heldout_b20"), ("language_b10_needcorr", "coverage_heldout_needcorr"),
                   ("v2_language_b10", "coverage_v2_heldout"), ("v2_numeracy_b10", "coverage_v2_heldout_numeracy")]:
        d = json.loads((RES / f"{f}.json").read_text())
        out[key] = {"pass": d["primary"]["pass"], **d["summary"]["fh"], "direct_coverage90": d["summary"]["direct"]["coverage90"],
                    "allocation": d["summary"]["allocation"]}
    return out


def _heldout_block_children() -> pd.DataFrame:
    rows = []
    for s in HELDOUT:
        w = make_world(s, dict(ASER2024_GOVT_STD3))
        g = w.schools.groupby("block_lgd").grade3_enrolment.sum()
        rows += [{"seed": s, "block_lgd": b, "children": int(n)} for b, n in g.items()]
    return pd.DataFrame(rows)


def separation_exploratory() -> dict:
    """POST HOC (not pre-registered): can +/-6 pp intervals tell blocks apart within a district?

    District average = child-weighted share (code-review issue 11). Matched baseline (hostile-judge v1 issue):
    share of blocks placed on the correct side of the district average by the moderated point estimate vs by raw reports.
    """
    b = pd.read_csv(RES / "coverage_heldout.blocks.csv")
    b = b[b.method == "fh"].merge(_heldout_block_children(), on=["seed", "block_lgd"])
    wavg = lambda col: b.groupby("seed").apply(lambda g: np.average(g[col], weights=g.children), include_groups=False)
    b = b.join(wavg("estimate").rename("d_est"), on="seed").join(wavg("true").rename("d_true"), on="seed").join(wavg("raw").rename("d_raw"), on="seed")
    below = b.hi < b.d_est; above = b.lo > b.d_est; flagged = below | above
    correct = (below & (b["true"] < b.d_true)) | (above & (b["true"] > b.d_true))
    true_below = b["true"] < b.d_true
    spread = b.groupby("seed")["true"].agg(lambda x: x.max() - x.min())
    return {"label": "post hoc, not pre-registered", "n_blocks": int(len(b)), "n_flagged": int(flagged.sum()),
            "share_flagged_below_or_above_average": float(flagged.mean()),
            "share_flags_on_correct_side": float(correct[flagged].mean()) if flagged.any() else float("nan"),
            "median_true_spread_within_district_pp": float(spread.median() * 100),
            "point_side_correct_moderated": float(((b.estimate < b.d_est) == true_below).mean()),
            "point_side_correct_raw": float(((b.raw < b.d_raw) == true_below).mean())}


def coverage_cluster_ci(reps: int = 4000, seed: int = 7, name: str = "coverage_heldout") -> dict:
    """POST HOC: world-level (cluster) bootstrap CI for held-out coverage; blocks within a district are dependent."""
    b = pd.read_csv(RES / f"{name}.blocks.csv")
    b = b[b.method == "fh"]
    per = b.groupby("seed").covered.agg(["sum", "size"])
    rng = np.random.default_rng(seed); k = per["sum"].to_numpy(); n = per["size"].to_numpy(); out = []
    for _ in range(reps):
        i = rng.integers(0, len(per), len(per)); out.append(k[i].sum() / n[i].sum())
    return {"label": "post hoc, world-level bootstrap over 30 held-out districts", "coverage": float(k.sum() / n.sum()),
            "ci95": [float(np.quantile(out, 0.025)), float(np.quantile(out, 0.975))], "reps": reps}


def demo_dashboard(seed: int = 1) -> dict:
    w = make_world(seed, dict(ASER2024_GOVT_STD3)); pub = w.public_view()
    risk = forensic_flags(pub.teacher_reports, pub.schools, pub.item_responses, pub.item_bank)
    b = round(0.10 * len(pub.schools))
    sel = select_audit(pub.schools, risk, b, "risk_pps", seed=seed + 17)
    aud = retest(w, sel, 12, seed=seed + 31)
    ctx, fit, iv = run_assurance(pub, risk, sel, aud, Design(budget=b), k_strata=4, R=200, seed=seed + 53, bias_model="mean")
    fh = iv[iv.method == "fh"].copy()
    raw = risk.assign(x=risk.reported_pct_meeting_goal * risk.grade3_enrolment).groupby("block_lgd").apply(lambda g: g.x.sum() / g.grade3_enrolment.sum(), include_groups=False)
    sch = pub.schools.groupby("block_lgd").agg(n_schools=("udise_code", "size"), children=("grade3_enrolment", "sum"))
    ret = sel.groupby("block_lgd").selected_for_audit.sum().rename("n_retested_schools")
    blocks = fh[["block_lgd", "estimate", "lo", "hi"]].join(raw.rename("raw"), on="block_lgd").join(sch, on="block_lgd").join(ret, on="block_lgd")
    meta = {"title": "Moderated block estimates — Grade 3 reading (SYNTHETIC)",
            "indicator": "Indicator: share of Grade 3 children who can read a Std II-level text (ASER-style proxy; not NIPUN attainment). "
                         "Moderated = teacher-reported census calibrated by an independent re-test of 10 % of schools; conservative 90 % intervals.",
            "footer": f"Synthetic district (seed {seed}), calibrated to ASER 2024 government-school Std III levels. No school-level labels are shown by design."}
    build_dashboard(blocks, meta, DEMO)
    return {"seed": seed, "blocks": int(len(blocks)), "eps_hat": fit.eps, "tau2_hat": fit.extras["tau2"]}


def held_out_auc() -> dict:
    aucs = []
    for s in HELDOUT:
        w = make_world(s, dict(ASER2024_GOVT_STD3)); pub = w.public_view()
        risk = forensic_flags(pub.teacher_reports, pub.schools, pub.item_responses, pub.item_bank)
        aucs.append(detection_auc(risk, w.truth_school))
    return {"mean": float(np.mean(aucs)), "sd": float(np.std(aucs, ddof=1)), "seeds": "101-130"}


def teacher_plan_demo(seed: int = 7) -> dict:
    w = make_world(seed, {**ASER2024_GOVT_STD3, "n_schools": 30, "n_clusters": 3})
    code = w.children.udise_code.value_counts().index[0]
    kids = w.children[w.children.udise_code == code]
    diags, roster = [], {}
    for i, (_, ch) in enumerate(kids.iterrows()):
        d, _used = adaptive_test(ch.student_raw_id, ch.udise_code, 3, "language", w.item_responses, w.item_bank, load_cutpoints("language"))
        diags.append(d); roster[d.student] = f"Roll {i + 1}"
    hi = make_plan(diags, roster, date(2026, 10, 5), channel="whatsapp", language="hi")
    en = make_plan(diags, roster, date(2026, 10, 5), channel="whatsapp", language="en")
    sms = make_plan(diags, roster, date(2026, 10, 5), channel="sms", language="hi")
    hdr = "SYNTHETIC — simulated class calibrated to ASER 2024 government-school Std III levels\n\n"
    (DEMO / "teacher_plan_hi.txt").write_text(hdr + hi.message_text + "\n", encoding="utf-8")
    (DEMO / "teacher_plan_en.txt").write_text(hdr + en.message_text + "\n", encoding="utf-8")
    (DEMO / "teacher_plan_sms_hi.txt").write_text(hdr + sms.message_text + "\n", encoding="utf-8")
    (DEMO / "teacher_plan_ivr.txt").write_text(hdr + render_ivr_script(sms) + "\n", encoding="utf-8")
    return {"class_size": int(len(kids)), "whatsapp_hi_bytes": hi.payload_bytes, "whatsapp_en_bytes": en.payload_bytes,
            "sms_hi_segments": sms_segments(sms), "groups": len(hi.groups)}


def governance() -> dict:
    from components.governance.evaluate import run_cases
    passed, total = run_cases()
    return {"passed": passed, "total": total}


def c4() -> dict:
    r = evaluate_seeds()
    return {k: {m: [float(v[0]), float(v[1])] for m, v in d.items()} for k, d in r.items()}


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True); DEMO.mkdir(parents=True, exist_ok=True)
    head = {"synthetic": True, "calibration": "ASER 2024 govt Std III: reading 0.234, subtraction 0.276 (eval/sim/calibration.py)",
            "coverage": coverage_results(), "coverage_cluster_ci": coverage_cluster_ci(), "coverage_v2_cluster_ci": coverage_cluster_ci(name="coverage_v2_heldout"), "separation_exploratory": separation_exploratory(), "detection_auc_heldout": held_out_auc(),
            "demo_dashboard": demo_dashboard(), "teacher_plan": teacher_plan_demo(), "governance": governance(), "c4_diagnostics": c4(),
            "command": "nice -n 10 python3 eval/run_eval.py"}
    (RES / "headline.json").write_text(json.dumps(head, indent=2) + "\n")
    cv = head["coverage"]; sep = head["separation_exploratory"]; c = head["c4_diagnostics"]
    lines = ["# SYNTHETIC evaluation summary", "", f"Command: `{head['command']}` (coverage runs: see `eval/preregistration/2026-10-04-coverage.md`).", "",
             "| Run (held-out: v1 seeds 101-130, v2 seeds 201-230; 180 blocks each) | 90% coverage | Wilson 95% | MAE moderated (pp) | MAE raw (pp) | mean half-width (pp) | allocation gain shown |",
             "|---|---:|---:|---:|---:|---:|---|"]
    for k, v in cv.items():
        lines.append(f"| {k} | {v['coverage90']:.3f} | {v['coverage_wilson95'][0]:.3f}–{v['coverage_wilson95'][1]:.3f} | {v['mae_pp']:.2f} | {v['raw_mae_pp']:.2f} | {v['mean_half_width_pp']:.2f} | {v['allocation']['gain_shown']} |")
    cc = head["coverage_cluster_ci"]
    lines += ["", f"Post hoc: world-level bootstrap 95% CI for held-out coverage {cc['coverage']:.3f}: {cc['ci95'][0]:.3f}–{cc['ci95'][1]:.3f}.",
              f"Post hoc separation (child-weighted district average): {sep['n_flagged']}/{sep['n_blocks']} blocks have intervals entirely below/above it; "
              f"{sep['share_flags_on_correct_side']:.2f} of those on the correct side; point estimates on the correct side: moderated {sep['point_side_correct_moderated']:.2f} vs raw {sep['point_side_correct_raw']:.2f}; "
              f"median true within-district spread {sep['median_true_spread_within_district_pp']:.1f} pp.",
              f"Detection AUC (held-out): {head['detection_auc_heldout']['mean']:.3f} ± {head['detection_auc_heldout']['sd']:.3f}.",
              f"C4 (seeds 101-105): CAT@8 exact level accuracy {c['adaptive_cat_8']['level_acc'][0]:.3f}; full-test Bayesian IRT {c['bayes_irt_full']['level_acc'][0]:.3f}; ASER rule {c['aser_rule_full']['level_acc'][0]:.3f}.",
              f"C7: Hindi WhatsApp plan {head['teacher_plan']['whatsapp_hi_bytes']} bytes for a class of {head['teacher_plan']['class_size']}; SMS {head['teacher_plan']['sms_hi_segments']} segments.",
              f"C12: {head['governance']['passed']}/{head['governance']['total']} policy cases pass."]
    (RES / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
