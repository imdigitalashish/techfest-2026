"""Score the final model on test with the FROZEN matcher of autoresearch/eval.py, i.e. the same code that produced
results/metrics_zeroshot.json, and merge both into results/metrics.json for an apples-to-apples comparison.
Part of the single final evaluation; nothing is selected or tuned on it.

    python -m t3det.frozen_compare <best.pt> <imgsz>
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from .paths import COMP, RESULTS


def main() -> None:
    w, imgsz = sys.argv[1], int(sys.argv[2])
    cfg = json.loads((COMP / "autoresearch" / "config.json").read_text())
    cfg["imgsz"] = imgsz
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(cfg, f)
    r = subprocess.run([sys.executable, str(COMP / "autoresearch" / "eval.py"), "--weights", w, "--config", f.name,
                        "--split", "test"], capture_output=True, text=True, cwd=COMP, env=os.environ.copy())
    if r.returncode:
        sys.exit(r.stderr[-1500:])
    sec = json.loads([ln for ln in r.stderr.splitlines() if ln.startswith("{")][-1])
    zs = json.loads((RESULTS / "metrics_zeroshot.json").read_text())
    m = json.loads((RESULTS / "metrics.json").read_text())
    m["frozen_matcher_test"] = {
        "what": "test scored with autoresearch/eval.py (greedy IoU>=0.5 match, COCO-style 101-point AP) - the same "
                "code as results/metrics_zeroshot.json",
        "trained": {k: sec[k] for k in ("mAP50", "boot_se", "precision@0.25", "recall@0.25", "n_gt")},
        "zero_shot": {"mAP50": zs["mAP50"], "precision@0.25": zs["precision"], "recall@0.25": zs["recall"],
                      "file": "results/metrics_zeroshot.json"},
        "config": cfg}
    (RESULTS / "metrics.json").write_text(json.dumps(m, indent=1) + "\n")
    print(json.dumps(m["frozen_matcher_test"]["trained"]), "zero-shot mAP50", zs["mAP50"])


if __name__ == "__main__":
    main()
