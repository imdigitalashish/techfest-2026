"""Fail if a computed number quoted in the proposal differs from the committed results (anti-drift check).

Each claim is a string that must appear verbatim in deliverables/round1-proposal.md, re-derived here from committed
files in eval/results/ and eval/public_data/derived/. Run: .venv/bin/python eval/check_docs.py (exit 1 on mismatch;
also run by pytest via tests/test_docs.py).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
R, D = ROOT / "eval" / "results", ROOT / "eval" / "public_data" / "derived"
PROPOSAL = ROOT / "deliverables" / "round1-proposal.md"


def j(name: str) -> dict:
    return json.loads((R / name).read_text())


def pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def claims() -> list[str]:
    out = []
    # C6 v0.3 pre-registered test (SYNTHETIC)
    a, runs = j("c6_v03_prereg_analysis.json"), j("c6_v03_prereg.json")["runs"]
    m, sd, v = a["means"], a["sds"], a["value_means"]
    for k in ["status_quo", "risk_bc", "best_arm_only", "rule", "challenger", "reference"]:
        out.append(f"| {m[k]:.2f} ± {sd[k]:.2f} | {v[k]:,.0f} |".replace("-0.", "−0."))
    h1, h2, s3 = a["H1_challenger_vs_rule"], a["H2_rule_vs_best_arm_only"], a["S3_perfect_linkage_challenger_minus_rule"]
    if a["H1_pass"]:
        out.append(f"by {h1['mean_diff']:.2f} of the reference gain (95% CI {h1['ci95'][0]:.2f}–{h1['ci95'][1]:.2f}; positive in {h1['seeds_positive']} of {h1['n']} worlds)")
    if a["H2_pass"]:
        out.append(f"beat best-arm-only by {h2['mean_diff']:.2f}")
    out += [f"deployed the challenger in {a['gate_pass_count']} of {h1['n']} worlds",
            f"the challenger's margin was {s3['mean_diff']:.2f}",
            f"about {int(round(a['pilot_train_mean'] / 5, -2)):,} pilot persons per arm"]
    if a["H3_pass"]:
        out.append("Women's floors, budgets and the holdout held in every world.")
    pe = j("policy_engine.json")
    out.append(f"{pe['correct']}/{pe['n_scenarios']} governance scenarios, {pe['false_allows']} false allows; "
               f"{pe['mutations_detected']}/{pe['n_mutations']} log-tampering attacks detected")
    pc = j("power_calc.json")
    out += [f"needs {pc['n_per_arm_individual']:,} persons per arm", f"about {pc['n_per_arm_clustered']:,} with BC clusters"]
    # Spike B (SYNTHETIC), four quarters of data
    sb = j("scorecard_spikeB.json")["runs"]["4"]
    rho = lambda k: float(np.mean([x["spearman_rho"][k] for x in sb]))
    out += [f"correlated {rho('M1_enrolments'):.2f} with their true contribution",
            f"\"operative\" share correlated {rho('M2_account_operative_share'):.2f}",
            f"incremental usage correlated **{rho('M4_sakriya_incremental'):.2f}**"]
    top = float(np.mean([x["share_of_gamers_in_top20"]["M4_sakriya_incremental"] for x in sb]))
    allg = sum(x["gaming_flags"]["gamers"] for x in sb) / (200 * len(sb))
    out.append(f"gamers were {100 * top:.0f}% of its top 20 against {100 * allg:.1f}% overall")
    # Hillstrom real RCT
    h = j("hillstrom_uplift.json")["runs"]
    d = [float(np.mean([x["budgets"][b]["diff_shrunk_vs_best_arm"]["per_1000"] for x in h])) for b in ("0.1", "0.2")]
    out.append(f"by {d[0]:.1f}–{d[1]:.1f} responses per 1,000")
    # Real public data
    t = pd.read_csv(D / "pmjdy_inoperative_trend.csv").set_index("as_of")
    out += [f"from {t.at['2021-03', 'inoperative_accounts_crore']:.2f} crore ({pct(t.at['2021-03', 'inoperative_share'])}, March 2021)",
            f"to {t.at['2025-12', 'inoperative_accounts_crore']:.2f} crore ({pct(t.at['2025-12', 'inoperative_share'])}, Lok Sabha answer of 8 December 2025)"]
    st = pd.read_csv(D / "pmjdy_inoperative_by_state_2025-07-31.csv")
    st["inoperative_share"] = st.inoperative_accounts / st.pmjdy_accounts  # exact, not the 4-dp rounded column
    lo, hi = st.loc[st.inoperative_share.idxmin()], st.loc[st.inoperative_share.idxmax()]
    big = st[st.pmjdy_accounts > 1e7]
    blo, bhi = big.loc[big.inoperative_share.idxmin()], big.loc[big.inoperative_share.idxmax()]
    up = st.set_index("state_ut").loc["Uttar Pradesh"]
    out += [f"{pct(lo.inoperative_share)} ({lo.state_ut}) to {pct(hi.inoperative_share)} ({hi.state_ut})",
            f"among the {len(big)} states with > 1 crore accounts, {pct(blo.inoperative_share)} ({blo.state_ut}) to {pct(bhi.inoperative_share)} ({bhi.state_ut})",
            f"Uttar Pradesh {up.inoperative_accounts / 1e7:.2f} crore ({pct(up.inoperative_share)})"]
    f = pd.read_csv(D / "findex2025_india_account_inactive.csv")
    g = lambda grp, y: float(f[(f.group2 == grp) & (f.year == y)].iloc[0]["inactive_t_d"] if grp == "all" else f[(f.group2 == grp) & (f.year == y)].iloc[0]["inactive_share_of_owners"])
    out += [f"{pct(g('all', 2021))} (2021) to {pct(g('all', 2024))} (2024)",
            f"{pct(g('women', 2024))} of women account owners had an inactive account against {pct(g('men', 2024))} of men",
            f"{pct(g('poorest 40%', 2024))} of the poorest 40% against {pct(g('richest 60%', 2024))} of the richest 60%"]
    return out


def main() -> int:
    text = PROPOSAL.read_text()
    bad = [c for c in claims() if c not in text]
    for c in bad:
        print("MISSING/DRIFTED:", c)
    print(f"check_docs: {len(claims()) - len(bad)}/{len(claims())} claims match committed results")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
