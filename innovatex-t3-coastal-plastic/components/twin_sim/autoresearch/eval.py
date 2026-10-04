"""FROZEN evaluator for the P2 dispatch ratchet. The loop never edits this file.

Prints ONE scalar on the first line: mean (over 20 fixed Monte Carlo draws, seed 20261004) of
escaped_kg summed over the 4 sites and the TUNING monsoons Jun-Sep 2019-2023, for the candidate
policy P2 = twin_sim/dispatch.py::p2_factory with twin_sim/p2_knobs.json, at the fixed crew budget
(2 crews x 8 h/day; asserted). Secondary metrics follow. Held-out years 2024-2025 are never touched.

Run: cd innovatex-t3-coastal-plastic/components && python twin_sim/autoresearch/eval.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from twin_sim import dispatch, sim  # noqa: E402

N_DRAWS, SEED = 20, 20261004
r = sim.evaluate("P2", sim.TUNE_YEARS, N_DRAWS, SEED)
assert np.allclose(r["crew_h"], dispatch.N_CREWS * dispatch.SHIFT_H * 122 * len(sim.TUNE_YEARS))
print(f"escaped_kg_mean {r['escaped'].mean():.1f}")
print(f"captured_fraction_mean {np.mean(1 - r['escaped'] / r['load']):.4f}")
print(f"overflow_site_hours_mean {r['overflow_h'].mean():.1f}")
print(f"crew_hours {r['crew_h'][0]:.0f}")
