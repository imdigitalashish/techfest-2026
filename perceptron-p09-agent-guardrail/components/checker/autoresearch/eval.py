"""FROZEN evaluator for the checker ratchet loop — never edited inside a loop.

Prints the dev score of the guard (default t0) on line 1, then one JSON line with secondaries and the
test-split regression check.  python -m components.checker.autoresearch.eval [guard]
"""
import json
import sys
from pathlib import Path

from eval.run_eval import run

guard = sys.argv[1] if len(sys.argv) > 1 else "t0"
RUNS = Path(__file__).parent / "runs"
dev = run(guard, "dev", out_dir=RUNS)["metrics"]
test = run(guard, "test", out_dir=RUNS)["metrics"]
print(f"{dev['score']:.4f}")
print(json.dumps({
    "dev": {k: dev[k] for k in ("catch_rate", "false_block_rate", "escalation_rate", "latency_ms_p95")},
    "test": {k: test[k] for k in ("score", "catch_rate", "false_block_rate", "escalation_rate", "latency_ms_p95")},
}))
