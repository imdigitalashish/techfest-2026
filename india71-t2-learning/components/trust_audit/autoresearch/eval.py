"""FROZEN evaluator for the measurement-assurance ratchet (do not edit inside the loop).

Prints: METRIC block_mae_pp_dev=<x>   CONSTRAINT coverage90_dev=<c>   (dev seeds 1-30, language, 10 % budget, SYNTHETIC)
"""
import subprocess
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def main() -> None:
    out = ROOT / ".cache" / "autoresearch_dev.json"
    subprocess.run([sys.executable, str(ROOT / "eval" / "coverage_test.py"), "--seeds", "1-30", "--out", str(out)], check=True, capture_output=True)
    d = json.loads(out.read_text())["summary"]["fh"]
    print(f"METRIC block_mae_pp_dev={d['mae_pp']:.3f}")
    print(f"CONSTRAINT coverage90_dev={d['coverage90']:.3f}")


if __name__ == "__main__":
    main()
