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
    ("**2W, CEA average, CO2e (central)**", "in2026_avg_co2e", "ev_scooter"),
    ("2W, CO2-only grid (understates grid emissions: upper bound on the EV saving)", "in2026_cea_average", "ev_scooter"),
    ("2W, operating margin, CO2e", "in2026_cea_operating_margin", "ev_scooter"),
    ("2W, build margin, CO2-only", "in2026_cea_build_margin", "ev_scooter"),
    ("2W, petrol tailpipe as E0 (no ethanol credit)", "in2026_petrol_e0", "ev_scooter"),
    ("**Car, CEA average, CO2e (central)**", "car_in2026_avg_co2e", "bev"),
    ("Car, central", "car_in2026_avg_co2e", "diesel"),
    ("Car, central", "car_in2026_avg_co2e", "cng"),
    ("Car, CO2-only grid (upper bound on the BEV saving)", "car_in2026_cea_average", "bev"),
    ("Car, operating margin, CO2e", "car_in2026_cea_operating_margin", "bev"),
    ("Car, build margin, CO2-only", "car_in2026_cea_build_margin", "bev"),
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


def table(d: dict) -> str:
    out = ["| Case and grid view | Reference (g CO2e/km, 90 %) | Alternative | Saving vs reference (90 %) | P(lower) |",
           "|---|---|---|---|---|"]
    for label, sid, alt in ROWS:
        s = d["scenarios"][sid]
        ref_id = next(iter(s["products"]))
        r, a, c = s["products"][ref_id], s["products"][alt], s["comparisons"][alt]
        out.append(f"| {label} | {r['label']} {r['total']:.1f} ({r['p05']:.1f}–{r['p95']:.1f}) | {a['label']} "
                   f"{a['total']:.1f} ({a['p05']:.1f}–{a['p95']:.1f}) | {saving(c)} | {c['p_lower']:.2f} |")
    out.append(f"\n_Rendered from `eval/results/latest.json` (inputs id `{d['inputs_id']}`, n = {d['n']}, seed {d['seed']}) by `eval/render_docs.py`._")
    return "\n".join(out)


def headline(d: dict) -> str:
    k = key_numbers(d)
    return (f"Central results (CEA FY2025-26 average grid, CO2e GWP100 (AR5, as ICCT inputs), partial upstream): e-scooter vs petrol scooter "
            f"saving **{k['2w_central']}**; e-Verito-class BEV sedan vs petrol sedan **{k['car_central']}** "
            f"(90 % intervals; inputs id `{k['inputs_id']}`).")


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
    bound = 3 / v["n_negative"] if v["n_negative"] else float("nan")
    fa = round(v["false_accept_rate"] * v["n_negative"])
    line = (f"quote presence: {round(v['found_rate'] * v['n_positive'])}/{v['n_positive']} quotes found; {fa} observed false accepts in "
            f"{v['n_negative']} synthetic digit-perturbed negatives (rule-of-three 95 % bound ≈ {100 * bound:.1f} %, not zero)")
    if vc.exists():
        line += "; " + vc.read_text().strip()
    return line + f" (verifier {v['verifier_version']})"


def render(text: str, d: dict) -> str:
    vl = verifier_line()
    if vl:
        text = re.sub(r"(<!-- verifier:begin -->).*?(<!-- verifier:end -->)", lambda m: m.group(1) + vl + m.group(2), text, flags=re.S)
    text = re.sub(r"(<!-- dbcounts:begin -->).*?(<!-- dbcounts:end -->)", lambda m: m.group(1) + dbcounts(d) + m.group(2), text, flags=re.S)
    text = re.sub(r"(<!-- results-table:begin -->\n).*?(\n<!-- results-table:end -->)", lambda m: m.group(1) + table(d) + m.group(2), text, flags=re.S)
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
