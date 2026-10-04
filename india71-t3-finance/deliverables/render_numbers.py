"""Generate deliverables/round1-proposal.md from round1-proposal.template.md, filling every computed number from
committed results (eval/results/*.json). Hand-edit the TEMPLATE, never the generated file.
Usage (from india71-t3-finance/): .venv/bin/python deliverables/render_numbers.py
"""
import json
import pathlib
import re

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = ROOT / "eval" / "results"
j = lambda f: json.loads((R / f).read_text())


def c5_claim() -> str:
    pe = j("policy_engine.json")
    return (f"a tested prototype: {pe['correct']}/{pe['n_scenarios']} governance scenarios, {pe['false_allows']} false allows; "
            f"{pe['mutations_detected']}/{pe['n_mutations']} log-tampering attacks detected; production needs authenticated identity "
            f"and externally published checkpoints")


def gamers() -> tuple[str, str]:
    sb = j("scorecard_spikeB.json")["runs"]["4"]
    top = float(np.mean([x["share_of_gamers_in_top20"]["M4_sakriya_incremental"] for x in sb]))
    allg = sum(x["gaming_flags"]["gamers"] for x in sb) / (200 * len(sb))
    return f"{100 * top:.0f}%", f"{100 * allg:.1f}%"


def power() -> tuple[str, str]:
    pc = j("power_calc.json")
    return f"{pc['n_per_arm_individual']:,}", f"{pc['n_per_arm_clustered']:,}"


def c6_section() -> str:
    a, runs = j("c6_v03_prereg_analysis.json"), j("c6_v03_prereg.json")["runs"]
    m, sd, v = a["means"], a["sds"], a["value_means"]
    rows = [("Status quo: BC visits to no-use, then dormant, then pass-through accounts", "status_quo"),
            ("Highest \"risk of non-use\" first (BC visit)", "risk_bc"),
            ("Best pilot arm per rupee to a random subset; rest of budget unspent", "best_arm_only"),
            ("**Transparent rule (default)**", "rule"),
            ("**Learned challenger** (same plan; model chooses whom to upgrade)", "challenger"),
            ("Reference allocation with true effects", "reference")]
    el = int(round(a["eligible_mean"], -2))
    tbl = [f"| Policy (budget Rs 10 per eligible person) | Share of reference gain (mean ± sd) | Extra persons in meaningful use (per ~{el:,} eligible) |",
           "|---|---|---|"]
    for label, k in rows:
        tbl.append(f"| {label} | {m[k]:.2f} ± {sd[k]:.2f} | {v[k]:,.0f} |".replace("-0.", "−0."))
    h1, h2, s3 = a["H1_challenger_vs_rule"], a["H2_rule_vs_best_arm_only"], a["S3_perfect_linkage_challenger_minus_rule"]
    per_arm = int(round(a["pilot_train_mean"] / 5, -2))
    val_n = int(round(a["gate_validation_mean"], -2))
    if a["H1_pass"]:
        h1_txt = (f"In a test registered before it was run, the learned challenger beat the transparent rule by {h1['mean_diff']:.2f} of the "
                  f"reference gain (95% CI {h1['ci95'][0]:.2f}–{h1['ci95'][1]:.2f}; positive in {h1['seeds_positive']} of {h1['n']} worlds)")
    else:
        h1_txt = (f"In a test registered before it was run, the learned challenger did **not** reliably beat the transparent rule "
                  f"(mean {h1['mean_diff']:+.2f}, 95% CI {h1['ci95'][0]:.2f}–{h1['ci95'][1]:.2f})")
    h2_txt = (f"; spending the leftover budget beat best-arm-only by {h2['mean_diff']:.2f}" if a["H2_pass"]
              else f"; spending the leftover budget did not reliably beat best-arm-only ({h2['mean_diff']:+.2f})")
    h3_txt = ("Budgets and the holdout held in every world, and the women's floor passed the registered check; a reviewer's strict "
              "re-check found one world one woman short of it (a holdout-rounding flaw, since fixed)." if a["H3_pass"]
              else "**A registered safeguard check failed** (see `eval/preregistration/c6_v03_results.md`).")
    gate_txt = (f"The gate, judging on about {val_n:,} held-out pilot persons, deployed the challenger in {a['gate_pass_count']} of {h1['n']} worlds, "
                f"so in practice the rule would have run{' everywhere' if a['gate_pass_count'] == 0 else ' elsewhere'}: the challenger's gain needs a larger pilot to be certified.")
    return f"""**4.5 What the working skeleton shows (all SYNTHETIC).** Ten simulated worlds of 50,000 persons, calibrated to the official PMJDY inoperative share; Jan Dhan holders not yet in meaningful use; the model sees only bank-observable proxies with error; person-level effects follow our assumptions:

{chr(10).join(tbl)}

_Share of reference gain = (policy − random) / (reference − random); the reference is a strong heuristic, not a certified optimum. Pre-registered test, seeds 20–29: `eval/preregistration/c6_v03.md` → `eval/results/c6_v03_prereg.json`._ **Dormancy is not persuadability**: dormancy-first outreach captures almost none of what the budget could achieve, and ranking by risk of non-use is worse than random. {h1_txt}{h2_txt}. {h3_txt} {gate_txt} With perfect person linkage the challenger's margin was {s3['mean_diff']:.2f}. Fitting used about {per_arm:,} pilot persons per arm; an earlier, smaller design picked the wrong arms in 2 of 10 worlds — pilot size is a design input. On a real 64,000-person randomised e-mail experiment [P9] (retail, not banking), the same learner beat "best message to a random subset" by 2.5–3.2 responses per 1,000 when only 10–20% could be contacted (CIs include zero in two of three splits) but lost at full coverage: target *who*, personalise *which* cautiously."""


def main():
    s = (ROOT / "deliverables" / "round1-proposal.template.md").read_text()
    gt, ga = gamers()
    ni, nc = power()
    for k, val in {"{{C5_CLAIM}}": c5_claim(), "{{GAMERS_TOP}}": gt, "{{GAMERS_ALL}}": ga, "{{N_IND}}": ni, "{{N_CL}}": nc,
                   "{{C6_SECTION}}": c6_section()}.items():
        assert k in s, k
        s = s.replace(k, val)
    assert not re.search(r"\{\{[A-Z0-9_]+\}\}", s), "unfilled placeholder"
    (ROOT / "deliverables" / "round1-proposal.md").write_text(s)
    print("wrote deliverables/round1-proposal.md")


if __name__ == "__main__":
    main()
