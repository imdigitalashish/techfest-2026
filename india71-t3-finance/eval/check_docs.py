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
    # C6 v0.2 pre-registered test (SYNTHETIC)
    r, a = j("c6_v02_prereg.json"), j("c6_v02_prereg_analysis.json")
    runs, m, sd = r["runs"], a["means"], a["sds"]
    for k in ["status_quo", "risk_bc", "best_arm_only", "rule", "challenger_who", "oracle"]:
        v = round(float(np.mean([x["policies"][k]["value"] for x in runs])))
        out.append(f"| {m[k]:.2f} ± {sd[k]:.2f} | {v} |".replace("-0.", "−0."))
    h1, h2 = a["H1_challenger_who_vs_rule"], a["H2_rule_vs_best_arm_only"]
    out += [f"in all {h1['seeds_positive']} worlds, by {h1['mean_diff']:.2f} of the achievable gain (95% CI {h1['ci95'][0]:.2f}–{h1['ci95'][1]:.2f})",
            f"beat best-arm-only by {h2['mean_diff']:.2f}",
            f"about {round(float(np.mean([x['gate']['n_validation'] for x in runs])), -1):.0f} validation persons per world",
            f"in {sum(1 for x in runs if x['policies']['rule']['normalised'] < 0.1)} of 10 worlds the pilot (about {round(float(np.mean([x['pilot_n'] for x in runs])) / 5, -1):.0f} persons per arm)",
            f"about {round(float(np.mean([x['pilot_n'] for x in runs])) / 5, -1):.0f} persons per arm can pick the wrong arm"]
    assert a["H1_pass"] and a["H2_pass"] and a["gate_pass_count"] == 0, "registered verdicts changed — rewrite the text"
    pe = j("policy_engine.json")
    out.append(f"implemented and tested: {pe['correct']}/{pe['n_scenarios']} governance scenarios, {pe['false_allows']} false allows; "
               f"tampering with the log detected in {pe['mutations_detected']}/{pe['n_mutations']} trials")
    # Spike B (SYNTHETIC), four quarters of data
    sb = j("scorecard_spikeB.json")["runs"]["4"]
    rho = lambda k: float(np.mean([x["spearman_rho"][k] for x in sb]))
    out += [f"correlated {rho('M1_enrolments'):.2f} with their true contribution",
            f"\"operative\" share correlated {rho('M2_account_operative_share'):.2f}",
            f"incremental usage correlated **{rho('M4_sakriya_incremental'):.2f}**"]
    # Hillstrom real RCT
    h = j("hillstrom_uplift.json")["runs"]
    d = [float(np.mean([x["budgets"][b]["diff_shrunk_vs_best_arm"]["per_1000"] for x in h])) for b in ("0.1", "0.2")]
    out.append(f"by {d[0]:.1f}–{d[1]:.1f} responses per 1,000")
    # Real public data
    t = pd.read_csv(D / "pmjdy_inoperative_trend.csv").set_index("as_of")
    out += [f"rose from {t.at['2021-03', 'inoperative_accounts_crore']:.2f} crore ({pct(t.at['2021-03', 'inoperative_share'])}, March 2021)",
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
