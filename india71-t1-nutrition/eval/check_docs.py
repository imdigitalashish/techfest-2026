"""Fail if a number quoted in the deliverables differs from the committed eval results (anti-drift check).

Each CLAIM pairs a string that must appear verbatim in a document with the value it is derived from.
Run: .venv/bin/python -m eval.check_docs        (exit code 1 on any mismatch; also run by pytest)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "eval" / "results"
PROPOSAL = ROOT / "deliverables" / "round1-proposal.md"
COMPONENTS = ROOT / "architecture" / "components.md"


def j(name: str) -> dict:
    return json.loads((R / name).read_text())


def f2(x: float) -> str:
    return f"{x:.2f}"


def claims() -> list[tuple[Path, str]]:
    gs, lk, cr, pd_, al = j("growth_standards.json"), j("identity_linkage.json"), j("credibility_engine.json"), j("pipeline_demo.json"), j("audit_ledger.json")
    pg, ew = j("policy_gate.json"), j("early_warning_v1.json")
    m = ew["methods"]
    ci = ew["bootstrap_95ci"]["lowest_observed_whz"]
    rule = m["lowest_observed_whz"]["episode_recall"]
    out = [
        (PROPOSAL, f"**{gs['value']} z**"),
        (PROPOSAL, f"{gs['n_points']:,} points"),
        (PROPOSAL, f"**{f2(lk['ids_only']['f1'])} / {f2(lk['plaintext_probabilistic']['f1'])} / {f2(lk['pprl_bloom']['f1'])}**"),
        (PROPOSAL, f"{lk['n_true_children']:,} children"),
        (PROPOSAL, f"**{f2(cr['auroc_nongood'])} / {f2(cr['auroc_fabricating'])}**"),
        (PROPOSAL, f"**{f2(rule)} ({f2(ci[0])}–{f2(ci[1])}) / {f2(m['logistic_anthro_plus_linked_health']['episode_recall'])} / "
                   f"{f2(m['rule_no_gain_2m']['episode_recall'])} / {f2(m['random_within_awc']['episode_recall'])}**"),
        (PROPOSAL, f"{m['lowest_observed_whz']['n_episodes']:,} new episodes"),
        (PROPOSAL, f"{round(100 * rule)}% of new wasting episodes"),
        (PROPOSAL, f"against {round(100 * m['rule_no_gain_2m']['episode_recall'])}% for the programme"),
        (PROPOSAL, f"{round(100 * m['random_within_awc']['episode_recall'])}% for random"),
        (PROPOSAL, f"model ({round(100 * m['logistic_anthro_plus_linked_health']['episode_recall'])}%)"),
        (PROPOSAL, f"{pd_['awcs']} AWCs, {pd_['children_measured_this_month']:,} children"),
        (PROPOSAL, f"**{pd_['tasks']:,} → {pd_['worklists']}; ≤{pd_['sms_max_chars']} chars; {'verified' if pd_['audit_chain_verified'] else 'FAILED'}**"),
        (PROPOSAL, f"**{pg['n_cases'] - pg['false_allows'] if pg['pass_rate'] == 1.0 else 'X'}/{pg['n_cases']} / "
                   f"{round(al['tamper_detection_rate'] * al['n_mutations'])}/{al['n_mutations']}**"),
        (COMPONENTS, f"**{rule:.3f}**"),
    ]
    cal = j("cohort_calibration.json")
    out.append((PROPOSAL, f"at-birth wasting is {round(100 * cal['at_birth_wasting'], 1)}%"))
    return out


def main() -> int:
    bad = 0
    for path, text in claims():
        ok = text in path.read_text()
        bad += not ok
        if not ok:
            print(f"MISMATCH {path.relative_to(ROOT)}: expected to contain {text!r}")
    print(f"check_docs: {len(claims()) - bad}/{len(claims())} quoted numbers match eval/results")
    return 1 if bad else 0


def test_docs_match_results():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
