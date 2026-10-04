"""ILLUSTRATIVE ESTIMATE, not a result: what the twin's relative changes would mean at one real BMC boom.

Inputs, each labelled:
  - REPORTED: monsoon catch per BMC boom, 2.5–3 t/day of mixed garbage (research/fact-check.md F12, Hindustan Times).
  - SIMULATED: share of arriving debris a boom retains under today's assumed roster, FWCE of P0 (twin, held-out).
  - SIMULATED: change in escaped kg, dispatch layer (P2 vs assumed roster P0), median and central 90% range.
  - SENSITIVITY: change in escaped kg, retrofit (20° angle + fail-open fuse + pocket halving re-float) vs today's geometry.
Arithmetic:
  escaping per boom-day ≈ catch × (1 − f) / f   (if the catch is the retained share f of what arrives)
  avoided per monsoon   ≈ escaping × (−relative change) × 122 days (1 Jun – 30 Sep)
The product inherits every assumption above (the capture curve is assumed, debris is not only plastic); the tow-tank
tests exist to replace these numbers. Reproduce: python3 innovatex-t3-coastal-plastic/eval/impact_estimate.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "eval" / "impact_estimate.json"
CATCH_T_PER_DAY = (2.5, 3.0)  # F12: "2.5–3 t/day in the monsoon" per boom (mixed garbage)
MONSOON_DAYS = 30 + 31 + 31 + 30  # June–September


def main() -> dict:
    an = json.loads((ROOT / "components/twin_sim/results/analysis.json").read_text())
    f = an["fwce"]["P0"]["fwce"]["median"]
    disp = an["paired_escaped_rel_diff"]["P2_vs_P0"]
    retro = an["boom_angle_sensitivity_P2"]["c_fuse_refloat_x0.5"]["theta20"]["escaped_rel_vs_current_a_theta90"]
    esc = [c * (1 - f) / f for c in CATCH_T_PER_DAY]

    def season(rel: float) -> list[float]:
        return [round(e * -rel * MONSOON_DAYS, 1) for e in esc]

    out = {
        "label": "ILLUSTRATIVE ESTIMATE (REPORTED catch x SIMULATED/SENSITIVITY ratios); not a result",
        "inputs": {"catch_t_per_day_monsoon": list(CATCH_T_PER_DAY), "catch_source": "research/fact-check.md F12",
                   "retained_share_f_P0_fwce": f, "monsoon_days": MONSOON_DAYS,
                   "dispatch_rel_P2_vs_P0": {k: disp[k] for k in ("median", "p05", "p95")},
                   "retrofit_rel_20deg_fuse_pocket": {k: retro[k] for k in ("median", "p05", "p95")}},
        "escaping_t_per_day": [round(e, 2) for e in esc],
        "dispatch_avoided_t_per_monsoon": {"median": season(disp["median"]), "p05": season(disp["p05"]),
                                           "p95": season(disp["p95"])},
        "retrofit_avoided_t_per_monsoon": {"median": season(retro["median"]), "p05": season(retro["p05"]),
                                           "p95": season(retro["p95"])},
        "note": "per boom; ranges run over the catch range (2.5 to 3 t/day); negative = more escapes. "
                "Debris is mixed garbage, not only plastic.",
        "reproduce": "python3 innovatex-t3-coastal-plastic/eval/impact_estimate.py",
    }
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    return out


if __name__ == "__main__":
    o = main()
    print(json.dumps({k: o[k] for k in ("escaping_t_per_day", "dispatch_avoided_t_per_monsoon",
                                         "retrofit_avoided_t_per_monsoon")}))
