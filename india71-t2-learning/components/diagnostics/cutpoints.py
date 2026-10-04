"""Frozen ability cut-points for the C4 diagnostic (code-review issue 3, gpt-6-sol).

Cut-points must never come from the evaluated world's latent ability. They are fixed once from DEVELOPMENT
worlds (seeds 1-5, ASER-calibrated simulator) and committed to cutpoints.json; in a real deployment they come
from a standard-setting / policy-linking exercise on the state's own items.
Regenerate: python3 components/diagnostics/cutpoints.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = Path(__file__).with_name("cutpoints.json")
DEV_SEEDS = (1, 2, 3, 4, 5)


def derive() -> dict:
    sys.path.insert(0, str(ROOT))
    import numpy as np
    from eval.sim.calibration import ASER2024_GOVT_STD3
    from eval.sim.world import make_world
    read, math = [], []
    for s in DEV_SEEDS:
        w = make_world(s, dict(ASER2024_GOVT_STD3))
        read.append(w.cfg["read_thresholds"]); math.append(w.cfg["math_thresholds"])
    return {"language": np.mean(read, axis=0).round(4).tolist(), "numeracy": np.mean(math, axis=0).round(4).tolist(),
            "provenance": f"mean of development-world cut-points, seeds {list(DEV_SEEDS)}, ASER-calibrated simulator (SYNTHETIC)"}


def load(subject: str) -> list[float]:
    return json.loads(PATH.read_text())[subject]


if __name__ == "__main__":
    d = derive(); PATH.write_text(json.dumps(d, indent=2) + "\n"); print(d)
