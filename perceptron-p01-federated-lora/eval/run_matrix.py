"""End-to-end eval harness (C9 driver): runs strategies × seeds for one scenario in one process.

Usage (from perceptron-p01-federated-lora/, venv active):
  python -m eval.run_matrix --scenario clean   --seeds 0 1 --tag v1
  python -m eval.run_matrix --scenario dropout --seeds 0 1 --tag v1
  python -m eval.summarize --tag v1            # → eval/results/v1_summary.md

Writes one JSON line per run to eval/results/<tag>_<scenario>.jsonl and the per-round log to
eval/results/logs/<tag>_<scenario>_<strategy>_s<seed>.json.
"""
from __future__ import annotations

import argparse
import json
import platform
import subprocess
from pathlib import Path

import torch

from components.aggregator import STRATEGIES
from components.orchestrator import ExperimentConfig, load_world, run_experiment

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "eval" / "results"


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default="clean", choices=["clean", "dropout"])
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1])
    ap.add_argument("--strategies", nargs="+", default=list(STRATEGIES))
    ap.add_argument("--rounds", type=int, default=12)
    ap.add_argument("--exclude", nargs="*", default=[])
    ap.add_argument("--tag", default="v1")
    args = ap.parse_args()

    (OUT / "logs").mkdir(parents=True, exist_ok=True)
    cfg0 = ExperimentConfig(scenario=args.scenario, rounds=args.rounds, exclude=tuple(args.exclude))
    lm, data = load_world(cfg0)
    env = {"commit": git_commit(), "torch": torch.__version__, "device": str(lm.device), "machine": platform.machine()}
    suffix = f"_ex{'-'.join(args.exclude)}" if args.exclude else ""
    out_jsonl = OUT / f"{args.tag}_{args.scenario}{suffix}.jsonl"
    for seed in args.seeds:
        for strat in args.strategies:
            cfg = ExperimentConfig(strategy=strat, scenario=args.scenario, seed=seed, rounds=args.rounds,
                                   exclude=tuple(args.exclude))
            summary, rounds_log = run_experiment(cfg, lm, data)
            summary["env"] = env
            with out_jsonl.open("a") as f:
                f.write(json.dumps(summary) + "\n")
            log_path = OUT / "logs" / f"{args.tag}_{args.scenario}{suffix}_{strat}_s{seed}.json"
            log_path.write_text(json.dumps(rounds_log))
            print(f"DONE {strat} {args.scenario} s{seed}: macro {summary['base_macro_loss']:.4f}→"
                  f"{summary['final_macro_loss']:.4f} worst={summary['final_worst_loss']:.4f} "
                  f"dom_c0={summary['dominance_c0']:.3f} err={summary['aggregation_error']:.3f} "
                  f"wall={summary['wall_s']:.0f}s", flush=True)


if __name__ == "__main__":
    main()
