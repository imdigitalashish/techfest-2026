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

from components.aggregator import BASE_STRATEGIES
from components.orchestrator import ExperimentConfig, load_world, run_experiment

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "eval" / "results"


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def data_provenance(data: dict, model_id: str) -> dict:
    """Digest of the exact token blocks used (train + eval, every domain) and the cached model snapshot revision."""
    import hashlib
    from pathlib import Path as _P

    h = hashlib.sha1()
    for d in sorted(data):
        for part in data[d]:
            h.update(d.encode())
            h.update(part.numpy().tobytes())
    ref = _P.home() / ".cache/huggingface/hub" / f"models--{model_id.replace('/', '--')}" / "refs" / "main"
    rev = ref.read_text().strip()[:12] if ref.exists() else "unknown"
    return {"data_digest": h.hexdigest()[:12], "model_revision": rev}


def code_provenance() -> dict:
    """sha1 over every .py file under components/ and eval/ (what actually ran), plus whether any differs from HEAD."""
    import hashlib

    h = hashlib.sha1()
    files = sorted(p for d in ("components", "eval") for p in (ROOT / d).rglob("*.py") if "__pycache__" not in p.parts)
    for p in files:
        h.update(str(p.relative_to(ROOT)).encode())
        h.update(p.read_bytes())
    try:
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain", "--", "components", "eval/run_matrix.py"],
                                             cwd=ROOT, text=True).strip())
    except Exception:
        dirty = True
    return {"code_sha": h.hexdigest()[:12], "dirty": dirty}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default="clean", choices=["clean", "dropout"])
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1])
    ap.add_argument("--strategies", nargs="+", default=list(BASE_STRATEGIES))
    ap.add_argument("--rounds", type=int, default=12)
    ap.add_argument("--exclude", nargs="*", default=[])
    ap.add_argument("--tag", default="v1")
    ap.add_argument("--alpha", type=float, default=32.0, help="PEFT lora_alpha (scale = alpha / r_max)")
    ap.add_argument("--skip-existing", action="store_true",
                    help="skip (strategy, seed) pairs already present in the output jsonl")
    args = ap.parse_args()

    (OUT / "logs").mkdir(parents=True, exist_ok=True)
    suffix = f"_ex{'-'.join(args.exclude)}" if args.exclude else ""
    out_jsonl = OUT / f"{args.tag}_{args.scenario}{suffix}.jsonl"
    done = set()
    if args.skip_existing and out_jsonl.exists():
        for line in out_jsonl.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                if r["rounds"] == args.rounds:
                    done.add((r["strategy"], r["seed"]))
    todo = [(seed, strat) for seed in args.seeds for strat in args.strategies if (strat, seed) not in done]
    if not todo:
        print("nothing to run", flush=True)
        return
    cfg0 = ExperimentConfig(scenario=args.scenario, rounds=args.rounds, exclude=tuple(args.exclude), alpha=args.alpha)
    lm, data = load_world(cfg0)
    env = {"commit": git_commit(), **code_provenance(), **data_provenance(data, cfg0.model_id),
           "torch": torch.__version__, "device": str(lm.device), "machine": platform.machine()}
    for seed, strat in todo:
        if True:
            cfg = ExperimentConfig(strategy=strat, scenario=args.scenario, seed=seed, rounds=args.rounds,
                                   exclude=tuple(args.exclude), alpha=args.alpha)
            summary, rounds_log = run_experiment(cfg, lm, data)
            summary["env"] = env
            with out_jsonl.open("a") as f:
                f.write(json.dumps(summary) + "\n")
            log_path = OUT / "logs" / f"{args.tag}_{args.scenario}{suffix}_{strat}_s{seed}.json"
            log_path.write_text(json.dumps(rounds_log))
            print(f"DONE {strat} {args.scenario} s{seed}: macro {summary['base_macro_loss']:.4f}→"
                  f"{summary['final_macro_loss']:.4f} worst={summary['final_worst_loss']:.4f} "
                  f"dom_c0={summary['dominance_c0']:.3f} err={summary['aggregation_error']:.3f} alpha={args.alpha:g} "
                  f"wall={summary['wall_s']:.0f}s", flush=True)


if __name__ == "__main__":
    main()
