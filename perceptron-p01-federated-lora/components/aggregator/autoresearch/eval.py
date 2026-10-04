"""FROZEN evaluator for the aggregator ratchet. Do not edit inside the auto-research loop.

Runs the fixed dropout scenario (12 rounds, SmolLM2-135M, 5 devices) for one strategy over the
seeds below and prints `METRIC <mean final macro loss>` plus guard metrics as JSON.
"""
from __future__ import annotations

import argparse
import json
import statistics

from components.orchestrator import ExperimentConfig, load_world, run_experiment

SEEDS = (0, 1)
ROUNDS = 12
SCENARIO = "dropout"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategy", default="anchor_full")
    ap.add_argument("--seeds", type=int, nargs="+", default=list(SEEDS))
    args = ap.parse_args()
    cfg0 = ExperimentConfig(strategy=args.strategy, scenario=SCENARIO, rounds=ROUNDS)
    lm, data = load_world(cfg0)
    rows = []
    for seed in args.seeds:
        cfg = ExperimentConfig(strategy=args.strategy, scenario=SCENARIO, rounds=ROUNDS, seed=seed)
        s, _ = run_experiment(cfg, lm, data, log=lambda *_: None)
        rows.append(s)
    out = {
        "strategy": args.strategy,
        "seeds": args.seeds,
        "final_macro_loss": statistics.mean(r["final_macro_loss"] for r in rows),
        "per_seed": [round(r["final_macro_loss"], 5) for r in rows],
        "final_worst_loss": statistics.mean(r["final_worst_loss"] for r in rows),
        "aggregation_error": max(r["aggregation_error"] for r in rows),
        "dominance_c0": statistics.mean(r["dominance_c0"] for r in rows),
        "weak_gain": statistics.mean(r["weak_gain"] for r in rows),
        "max_spike": max(r["max_spike"] for r in rows),
    }
    print(json.dumps(out))
    print(f"METRIC {out['final_macro_loss']:.5f}")


if __name__ == "__main__":
    main()
