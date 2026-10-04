#!/usr/bin/env python3
"""Assert the qualitative claims made in the deliverables against committed results (complements check_numbers.py).

Usage: python scripts/check_claims.py --tag v2      (exit 1 if any claim is not supported)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOMS = ["wiki", "pycode", "cheaders", "readmes", "manpages"]
BASELINES = ["fedavg_ab_homo", "ffa_lora", "flexlora"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="v2")
    args = ap.parse_args()
    res = ROOT / "eval" / "results"
    c = json.loads((res / f"{args.tag}_canonical.json").read_text())
    d = json.loads((res / f"{args.tag}_dropout_canonical.json").read_text())
    S, A = "dropout", "anchor_full"
    claims = {
        "every headline comparison has 5 shared seeds":
            all(c[f"{S}.spike_vs_{b}.n"] == 5 for b in BASELINES),
        "AnchorLoRA macro loss lower than each baseline (95% CI upper bound < 0)":
            all(c[f"{S}.spike_vs_{b}.macro_hi"] < 0 for b in BASELINES),
        "all five AnchorLoRA mean domain losses decrease vs untuned":
            all(c[f"{S}.{A}.{dm}.gain_mean"] > 0 for dm in DOMS),
        "AnchorLoRA: all five Bonferroni lower bounds > 0 (rendered as a count)":
            c[f"{S}.{A}.domains_ci_pos_bonf"] == 5,
        "every baseline improves only the data-rich domain; other four regress (Bonferroni upper bound < 0)":
            all(c[f"{S}.{b}.wiki.gain_lo_bonf"] > 0 and all(c[f"{S}.{b}.{dm}.gain_hi_bonf"] < 0 for dm in DOMS[1:])
                for b in BASELINES),
        "under the starter, all four non-data-rich domains end worse than untuned (means)":
            all(c[f"{S}.fedavg_ab_homo.{dm}.gain_mean"] < 0 for dm in DOMS[1:]),
        "AnchorLoRA sample-weighted (micro) loss is worse than the starter's (CI lower bound > 0)":
            c[f"{S}.spike_vs_fedavg_ab_homo.micro_lo"] > 0,
        "AnchorLoRA worst-domain loss is higher than the starter's (CI lower bound > 0)":
            c[f"{S}.spike_vs_fedavg_ab_homo.worst_lo"] > 0,
        "outage device's domain below untuned at every evaluated checkpoint in every AnchorLoRA seed":
            d[f"{S}.{A}.outage_peak_rise_max"] < 0,
        "outage device's domain rose above untuned under the starter (mean peak > 0)":
            d[f"{S}.fedavg_ab_homo.outage_peak_rise_mean"] > 0,
        "data-rich device's mean norm share: starter > 0.5 > AnchorLoRA":
            c[f"{S}.fedavg_ab_homo.c0_norm_mean"] > 0.5 > c[f"{S}.{A}.c0_norm_mean"],
        "AnchorLoRA aggregation exact (mean relative residual < 1e-5)":
            c[f"{S}.{A}.agg_err_mean"] < 1e-5,
    }
    bad = 0
    for text, ok in claims.items():
        print(f"{'OK  ' if ok else 'FAIL'} {text}")
        bad += not ok
    print(f"{'PASS' if not bad else 'FAIL'}: {len(claims) - bad}/{len(claims)} claims supported")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
