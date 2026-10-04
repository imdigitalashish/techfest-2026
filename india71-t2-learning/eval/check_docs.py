"""Fail if a number quoted in the deliverables differs from the committed results (anti-drift check).

Each claim pairs a string that must appear verbatim in a document with the committed value it comes from.
Run (from india71-t2-learning/): python3 eval/check_docs.py   (exit 1 on any mismatch; also collected by pytest)
Sources: eval/results/headline.json (python3 eval/run_eval.py), eval/results/coverage_heldout*.json
(pre-registered: eval/preregistration/2026-10-04-coverage.md), data/public/*.csv, eval/results/real_data_analysis.md.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "eval" / "results"
PROPOSAL = ROOT / "deliverables" / "round1-proposal.md"


def _f(x: float, n: int = 1) -> str:
    return f"{x:.{n}f}"


def claims() -> list[tuple[Path, str]]:
    h = json.loads((RES / "headline.json").read_text())
    cv = h["coverage"]; b10 = cv["language_b10"]; sep = h["separation_exploratory"]; c4 = h["c4_diagnostics"]; tp = h["teacher_plan"]; gv = h["governance"]
    al = b10["allocation"]; al5 = cv["language_b05"]["allocation"]
    rda = (RES / "real_data_analysis.md").read_text()
    m_read = re.search(r"ASER govt Std III reading vs PARAKH Grade 3 Language \| 27 \| [0-9.]+ \| ([0-9.]+)", rda)
    m_math = re.search(r"ASER govt Std III subtraction vs PARAKH Grade 3 Mathematics \| 27 \| [0-9.]+ \| ([0-9.]+)", rda)
    m_loso = re.search(r"PARAKH Language -> ASER reading \| 27 \| ([0-9.]+) \| ([0-9.]+)", rda)
    v2 = cv["v2_language_b10"]; al2 = v2["allocation"]; cc = h["coverage_cluster_ci"]
    m = lambda x: x.replace("-", "−")  # proposal uses the Unicode minus sign
    out = [
        (PROPOSAL, f"**{_f(b10['raw_mae_pp'], 2)} → {_f(b10['mae_pp'], 2)} pp** / **{_f(v2['raw_mae_pp'], 2)} → {_f(v2['mae_pp'], 2)} pp**"),
        (PROPOSAL, f"**{_f(100 * b10['coverage90'])} %** / **{_f(100 * v2['coverage90'])} %**; **±{_f(b10['mean_half_width_pp'])} pp** "
                   f"(district-clustered 95 % CI for v1: {_f(100 * cc['ci95'][0])}–{_f(100 * cc['ci95'][1])} %)"),
        (PROPOSAL, f"±{_f(cv['language_b05']['mean_half_width_pp'])} / ±{_f(b10['mean_half_width_pp'])} / ±{_f(cv['language_b20']['mean_half_width_pp'])} pp"),
        (PROPOSAL, f"{sep['n_flagged']} of {sep['n_blocks']}, {'all' if sep['share_flags_on_correct_side'] == 1.0 else 'X'} on the correct side, but raw reports rank blocks as well "
                   f"({round(100 * sep['point_side_correct_raw'])} % vs {round(100 * sep['point_side_correct_moderated'])} % on the correct side)"),
        (PROPOSAL, m(f"(v1: {al['diff_moderated_minus_raw_mean']:+.1f} children, CI {al['diff_ci95'][0]:.1f} to {al['diff_ci95'][1]:+.1f})")),
        (PROPOSAL, m(f"in v2 ({al2['diff_moderated_minus_raw_mean']:.1f}, CI {al2['diff_ci95'][0]:.1f} to {al2['diff_ci95'][1]:.1f})")),
        (PROPOSAL, f"{_f(c4['adaptive_cat_8']['level_acc'][0], 3)}, vs {_f(c4['bayes_irt_full']['level_acc'][0], 3)} for the full test"),
        (PROPOSAL, f"{tp['whatsapp_hi_bytes']}-byte Hindi message, {tp['sms_hi_segments']} SMS / {gv['passed']} of {gv['total']} pass"),
        (PROPOSAL, f"(Spearman ρ = {_f(float(m_read.group(1)), 2)}; maths ρ = {_f(float(m_math.group(1)), 2)})"),
        (PROPOSAL, f"(out-of-state error {_f(float(m_loso.group(1)))} vs {_f(float(m_loso.group(2)))} points)"),
        (PROPOSAL, "600 schools, 6 blocks"),
        (PROPOSAL, "(30 each, 180 blocks)"),
    ]
    assert al2["diff_ci95"][1] < 0, "v2 allocation is claimed to be worse"
    # allocation at 5 % must be worse (CI entirely below 0) for the sentence "at a 5 % budget it is worse"
    out.append((PROPOSAL, "and at a 5 % budget, so school figures are not used for targeting" if al5["diff_ci95"][1] < 0 else "CLAIM-NOT-SUPPORTED: 5% allocation worse"))
    # calibration targets quoted in the proposal must equal the simulator calibration
    cal = (ROOT / "eval" / "sim" / "calibration.py").read_text()
    for v in ("0.234", "0.276"):
        out.append((ROOT / "eval" / "sim" / "calibration.py", v))
    assert "0.234" in cal and "0.276" in cal
    out.append((PROPOSAL, "**23.4 %**")); out.append((PROPOSAL, "**27.6 %**"))
    return out


def main() -> int:
    bad = 0
    cl = claims()
    for path, text in cl:
        ok = text in path.read_text(encoding="utf-8")
        bad += not ok
        if not ok:
            print(f"MISMATCH {path.relative_to(ROOT)}: expected to contain {text!r}")
    print(f"check_docs: {len(cl) - bad}/{len(cl)} quoted numbers match committed results")
    return 1 if bad else 0


def test_docs_match_results():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
