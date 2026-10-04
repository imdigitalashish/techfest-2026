"""Render results tables into the deliverables from eval/results/latest.json, so documents cannot drift from the run.

Usage (from ev-c2-green-auto-lca/):  python3 eval/render_docs.py      # rewrites marked blocks in place
Blocks: <!-- results-table:begin --> ... <!-- results-table:end -->  (methodology §10)
        <!-- headline:begin --> ... <!-- headline:end -->            (one-line headline, any document)
Then run `python3 eval/check_docs.py` (also part of the tests) to verify nothing stale remains.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ["deliverables/round1-methodology.md", "deliverables/round1-roadmap.md", "README.md", "thought_node.md",
        "architecture/adr/001-spike.md", "research/landscape.md"]
ROWS = [  # (label, scenario, alternative product) — reference product is the scenario's first product
    ("**Car, CEA average grid, partial-upstream CO2e (central)**", "car_in2026_avg_co2e", "bev"),
    ("Car, central — diesel", "car_in2026_avg_co2e", "diesel"),
    ("Car, central — CNG (methane-slip range 60–1000 mg/km skews the draws)", "car_in2026_avg_co2e", "cng"),
    ("Car, one battery replacement (structural sensitivity)", "car_in2026_battery_replacement", "bev"),
    ("Car, transmission-only losses (lower bound on technical losses)", "car_in2026_tx_losses", "bev"),
    ("Car, CO2-only panel — CEA average", "car_in2026_cea_average", "bev"),
    ("Car, CO2-only panel — CEA operating margin", "car_in2026_om_co2_only", "bev"),
    ("Car, CO2-only panel — CEA build margin", "car_in2026_cea_build_margin", "bev"),
    ("Car, CEA operating margin, partial-upstream CO2e", "car_in2026_cea_operating_margin", "bev"),
    ("**2W, CEA average grid (central; partial, mixed-basis indicator)**", "in2026_avg_co2e", "ev_scooter"),
    ("2W, one battery replacement (structural sensitivity)", "in2026_battery_replacement", "ev_scooter"),
    ("2W, transmission-only losses", "in2026_tx_losses", "ev_scooter"),
    ("2W, CO2-only panel — CEA average", "in2026_cea_average", "ev_scooter"),
    ("2W, CO2-only panel — CEA operating margin", "in2026_om_co2_only", "ev_scooter"),
    ("2W, CO2-only panel — CEA build margin", "in2026_cea_build_margin", "ev_scooter"),
    ("2W, CEA operating margin, partial-upstream CO2e", "in2026_cea_operating_margin", "ev_scooter"),
    ("2W, petrol tailpipe as E0 (no ethanol credit)", "in2026_petrol_e0", "ev_scooter"),
]


def pct(x: float) -> str:
    return f"{100 * x:.1f}"


def saving(c: dict) -> str:
    lo, hi = c["reduction_90pct"]
    return f"{pct(c['reduction_central'])} % ({pct(lo)} to {pct(hi)})"


def key_numbers(d: dict) -> dict[str, str]:
    s2, sc = d["scenarios"]["in2026_avg_co2e"], d["scenarios"]["car_in2026_avg_co2e"]
    return {"2w_central": saving(s2["comparisons"]["ev_scooter"]),
            "car_central": saving(sc["comparisons"]["bev"]),
            "verif_2w": f"{d['headline']['verification_mape_pct_2w']:.2f} %",
            "verif_car": f"{d['headline']['verification_mape_pct_car']:.1f} %",
            "inputs_id": d["inputs_id"]}


def basis(s: dict) -> str:
    return "harmonized: " + s["gas_basis_families"][0] if s["harmonized"] else "MIXED: " + ", ".join(s["gas_basis_families"])


def table(d: dict) -> str:
    out = ["| Case and grid view | Gas basis | Reference (g/km, 90 %) | Alternative (g/km, 90 %) | Saving vs reference: central (5th–95th pct) | P(lower) |",
           "|---|---|---|---|---|---|"]
    for label, sid, alt in ROWS:
        s = d["scenarios"][sid]
        ref_id = next(iter(s["products"]))
        r, a, c = s["products"][ref_id], s["products"][alt], s["comparisons"][alt]
        out.append(f"| {label} | {basis(s)} | {r['label']} {r['total']:.1f} ({r['p05']:.1f}–{r['p95']:.1f}) | {a['label']} "
                   f"{a['total']:.1f} ({a['p05']:.1f}–{a['p95']:.1f}) | {saving(c)} | {c['p_lower']:.4f} |")
    out.append(f"\n_Rendered from `eval/results/latest.json` (inputs id `{d['inputs_id']}`, n = {d['n']}, seed {d['seed']}) by `eval/render_docs.py`. "
               "Central = plug-in calculation with the listed point inputs; interval = 5th–95th percentile of paired draws from the stated input "
               "distributions; P(lower) = fraction of draws in which the alternative is lower. Model-conditional, not calibrated coverage; structural "
               "choices (boundary, grid method, lifetime) are shown as separate rows, not inside the intervals._")
    return "\n".join(out)


def manifest(d: dict) -> str:
    return f"inputs id `{d['inputs_id']}`, n = {d['n']} paired Monte Carlo draws, seed {d['seed']}"


def headline(d: dict) -> str:
    k = key_numbers(d)
    sc, s2 = d["scenarios"]["car_in2026_avg_co2e"], d["scenarios"]["in2026_avg_co2e"]
    return (f"Central results (CEA FY2025-26 average grid, partial upstream, {manifest(d)}): the legacy-data sedan case is {basis(sc)} — "
            f"e-Verito-class BEV vs petrol sedan saving **{k['car_central']}**, P(lower) {sc['comparisons']['bev']['p_lower']:.2f} (not decisive). "
            f"The scooter calculation gives **{k['2w_central']}** lower emissions in a **partial, mixed-basis GHG indicator** "
            f"({', '.join(s2['gas_basis_families'])}), not yet a harmonized GWP100 comparison.")


def dbcounts(d: dict) -> str:
    db = d["db"]
    st = db["by_status"]
    return (f"{db['records']} records ({st.get('verified', 0)} verified, {st.get('derived', 0)} derived) "
            f"from {db['sources']} opened sources")


def verifier_line() -> str | None:
    vj, vc = ROOT / "eval/results/verifier.json", ROOT / "eval/results/value_check.txt"
    if not vj.exists():
        return None
    v = json.loads(vj.read_text())
    fa = round(v["false_accept_rate"] * v["n_negative"])
    line = (f"quote presence: {round(v['found_rate'] * v['n_positive'])}/{v['n_positive']} quotes found; the verifier accepted {fa} of "
            f"{v['n_negative']} synthetic digit-perturbed regression cases (clustered, reused and not sampled from deployment errors, so this "
            f"does not estimate or bound the deployment false-accept rate)")
    if vc.exists():
        line += "; " + vc.read_text().strip()
    return line + f" (verifier {v['verifier_version']})"


def synthetic_line() -> str:
    vj = ROOT / "eval/results/verifier.json"
    n = json.loads(vj.read_text())["n_negative"] if vj.exists() else "the"
    return (f"No synthetic inventory or vehicle-performance records are used in the case studies. Verifier evaluation uses {n} labelled "
            "synthetic digit-perturbed quote negatives generated from source records. Monte Carlo draws simulate the stated uncertainty model "
            "and are not measured data. Any future synthetic inventory record will carry status `synthetic`.")


def render(text: str, d: dict) -> str:
    text = re.sub(r"(<!-- synthetic:begin -->).*?(<!-- synthetic:end -->)", lambda m: m.group(1) + synthetic_line() + m.group(2), text, flags=re.S)
    vl = verifier_line()
    if vl:
        text = re.sub(r"(<!-- verifier:begin -->).*?(<!-- verifier:end -->)", lambda m: m.group(1) + vl + m.group(2), text, flags=re.S)
    text = re.sub(r"(<!-- dbcounts:begin -->).*?(<!-- dbcounts:end -->)", lambda m: m.group(1) + dbcounts(d) + m.group(2), text, flags=re.S)
    text = re.sub(r"(<!-- results-table:begin -->).*?(<!-- results-table:end -->)", lambda m: m.group(1) + "\n" + table(d) + "\n" + m.group(2), text, flags=re.S)
    text = re.sub(r"(<!-- manifest:begin -->).*?(<!-- manifest:end -->)", lambda m: m.group(1) + manifest(d) + m.group(2), text, flags=re.S)
    text = re.sub(r"(<!-- headline:begin -->).*?(<!-- headline:end -->)", lambda m: m.group(1) + headline(d) + m.group(2), text, flags=re.S)
    return text


def main() -> None:
    d = json.loads((ROOT / "eval/results/latest.json").read_text())
    for rel in DOCS:
        p = ROOT / rel
        if p.exists():
            t = p.read_text()
            n = render(t, d)
            if n != t:
                p.write_text(n)
                print(f"rendered {rel}")


if __name__ == "__main__":
    main()
