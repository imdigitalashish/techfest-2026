from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from components.diagnostics.evaluate import scalar_c4_level_acc_at_8_items


def main() -> None:
    parser = argparse.ArgumentParser(description="Frozen scalar evaluator for C4 CAT autoresearch.")
    parser.add_argument("--seeds", default="101,102,103,104,105", help="Comma-separated integer seeds")
    args = parser.parse_args()
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    metric = scalar_c4_level_acc_at_8_items(seeds)
    print(f"METRIC c4_level_acc_at_8_items={metric:.6f}")


if __name__ == "__main__":
    main()
