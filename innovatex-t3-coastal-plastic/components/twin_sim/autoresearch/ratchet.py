"""Autoresearch ratchet for P2 (karpathy/autoresearch-style keep-if-better loop).

Each hypothesis patches twin_sim/p2_knobs.json (P2's parameters and logic switches), runs the FROZEN
eval.py, keeps the patch only if escaped_kg_mean drops by more than KEEP_REL (0.1%), else reverts.
Every run is appended to results.tsv. Held-out years are never evaluated here.

Run: cd innovatex-t3-coastal-plastic/components && python twin_sim/autoresearch/ratchet.py
"""
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
KNOBS = HERE.parent / "p2_knobs.json"
TSV = HERE / "results.tsv"
KEEP_REL = 0.001
HYPOTHESES = [
    ({"tide_aware": False}, "ablation: fixed 08:30 IST shift instead of tide-aware start"),
    ({"w_bypass": 0.0}, "forecast bypass risk adds nothing"),
    ({"w_bypass": 5.0}, "clear harder before forecast flood release"),
    ({"w_over": 0.0}, "overflow probability adds nothing"),
    ({"w_over": 3.0}, "prioritise forecast overtopping more"),
    ({"w_arrival": 0.0}, "ignore forecast arrivals (sensed fill only)"),
    ({"w_arrival": 1.0}, "count full expected capture of next-24h arrivals"),
    ({"w_arrival": 2.0}, "over-weight expected arrivals"),
    ({"arr_horizon": 48}, "use 48 h forecast arrivals"),
    ({"loss_weight": 1.0}, "weight sites by predicted ebb leakage (1 - e_cap)"),
    ({"loss_weight": 3.0}, "strong leakage weighting"),
    ({"w_stock": 0.5}, "less weight on plain stored kg"),
    ({"w_stock": 2.0}, "more weight on plain stored kg"),
]


ROUND2 = [
    ({"w_arrival": 0.0, "w_over": 0.0, "w_bypass": 0.0}, "round2: forecast terms off together (pure tide-aware kg greedy)"),
    ({"w_arrival": 0.25}, "round2: light weight on forecast arrivals"),
    ({"w_over": 0.5}, "round2: lighter overflow weight"),
    ({"starts_utc": [2, 3, 4, 5]}, "round2: narrower daylight start window (07:30-10:30 IST)"),
]


def run_eval() -> float:
    out = subprocess.check_output([sys.executable, str(HERE / "eval.py")], text=True,
                                  cwd=str(HERE.parents[1]))
    return float(out.splitlines()[0].split()[1]), out.strip().replace("\n", "; ")


def sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()


def log(row):
    new = not TSV.exists()
    with TSV.open("a") as f:
        if new:
            f.write("timestamp\tcommit\thypothesis\tmetric\tdelta\tkept\tnotes\n")
        f.write("\t".join(str(x) for x in row) + "\n")


def main(passes: int = 2):
    best_knobs = json.loads(KNOBS.read_text())
    best, notes = run_eval()
    log([time.strftime("%Y-%m-%dT%H:%M:%S%z"), sha(), "baseline P2 (current p2_knobs.json)", f"{best:.1f}", "0",
         "baseline", notes])
    for p in range(passes):
        for patch, why in (ROUND2 if "--round2" in sys.argv else HYPOTHESES):
            cand = dict(best_knobs, **patch)
            if cand == best_knobs:
                continue
            KNOBS.write_text(json.dumps(cand, indent=1))
            m, notes = run_eval()
            kept = m < best * (1 - KEEP_REL)
            log([time.strftime("%Y-%m-%dT%H:%M:%S%z"), sha() + "+knobs", f"pass{p + 1}: {json.dumps(patch)} {why}",
                 f"{m:.1f}", f"{m - best:+.1f}", "yes" if kept else "no", notes])
            print(f"{'KEEP' if kept else 'drop'} {m:.1f} ({m - best:+.1f}) {patch}", flush=True)
            if kept:
                best, best_knobs = m, cand
            else:
                KNOBS.write_text(json.dumps(best_knobs, indent=1))
    KNOBS.write_text(json.dumps(best_knobs, indent=1))
    print("best", best, best_knobs)


if __name__ == "__main__":
    main(passes=1 if "--round2" in sys.argv else 2)
