"""Dropout-stretch analysis from per-round logs (no GPU): what happens to each device's contribution and to
the outage device's domain during a mid-run outage.

Usage: python -m eval.dropout_analysis --tag v1   → eval/results/<tag>_dropout_analysis.md
"""
from __future__ import annotations

import argparse
import glob
import json
import statistics
from collections import defaultdict
from pathlib import Path

from components.device_simulator import DEFAULT_PROFILES

OUT = Path(__file__).resolve().parent / "results"
SYMBOL = {"ok": "o", "partial": "p", "offline": "-", "late_discarded": "x"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="v1")
    args = ap.parse_args()
    base = json.load(open(OUT / "base_per_domain_smollm2-135m.json"))
    dom = {p.client_id: p.domain for p in DEFAULT_PROFILES}
    outage = {p.client_id: p.outage_rounds for p in DEFAULT_PROFILES if p.outage_rounds}
    rows, contrib = [], defaultdict(lambda: defaultdict(list))
    peak = defaultdict(list)
    for f in sorted(glob.glob(str(OUT / "logs" / f"{args.tag}_dropout_*_s*.json"))):
        name = Path(f).stem[len(f"{args.tag}_dropout_"):]
        strat, seed = name.rsplit("_s", 1)
        log = json.load(open(f))
        for cid in dom:
            used = sum(1 for e in log for u in e["updates"]
                       if u["client_id"] == cid and u["status"] in ("ok", "partial"))
            mem = sum(1 for e in log if cid in e["aggregation"].get("used_memory_for", []))
            contrib[strat][cid].append((used, mem))
        for cid, rounds in outage.items():
            status = "".join(SYMBOL[[u for u in e["updates"] if u["client_id"] == cid][0]["status"]] for e in log)
            traj = [(e["round"], e["eval"]["per_domain_loss"][dom[cid]]) for e in log if "eval" in e]
            pk = max(v for _, v in traj) - base[dom[cid]]
            peak[strat].append(pk)
            rows.append(f"| {strat} | {seed} | `{status}` | " + " · ".join(f"r{r}: {v:.4f}" for r, v in traj)
                        + f" | {pk:+.4f} | {traj[-1][1] - base[dom[cid]]:+.4f} |")
    cid0 = next(iter(outage))
    lines = [f"# Dropout stretch analysis `{args.tag}` (auto-generated: `python -m eval.dropout_analysis --tag {args.tag}`)", "",
             f"Scenario `dropout`: device {cid0} ({dom[cid0]}) is offline in rounds {outage[cid0][0] + 1}–{outage[cid0][-1] + 1} "
             "(1-based), on top of random offline rounds and deadline cut-offs. Status per round: o = full work, p = partial "
             "work accepted, x = cut off and discarded, - = offline. Untuned-model loss on its domain: "
             f"**{base[dom[cid0]]:.4f}**.", "",
             f"| Strategy | seed | {cid0} status r1–r12 | {dom[cid0]} loss at evaluations | peak vs untuned | final vs untuned |",
             "|---|---|---|---|---|---|"] + rows
    lines += ["", "Rounds in which each device's work entered the aggregate (mean over seeds; + memory = rounds its last "
              "update was reused while absent):", "",
              "| Strategy | " + " | ".join(f"{c} ({dom[c]})" for c in dom) + " |", "|---" * (len(dom) + 1) + "|"]
    for strat, per in sorted(contrib.items()):
        cells = []
        for c in dom:
            used = statistics.mean(u for u, _ in per[c])
            mem = statistics.mean(m for _, m in per[c])
            cells.append(f"{used:.1f}" + (f" + {mem:.1f}" if mem else ""))
        lines.append(f"| {strat} | " + " | ".join(cells) + " |")
    lines += ["", "Peak rise of the outage device's domain loss above the untuned model (mean over seeds): "
              + "; ".join(f"{s} {statistics.mean(v):+.4f} (n={len(v)})" for s, v in sorted(peak.items())), ""]
    (OUT / f"{args.tag}_dropout_analysis.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
