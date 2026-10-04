"""Contract test for eval v3's reference geodesic: a long wall with one doorway; clearance r=0.25 inflates the
wall into a slab of half-width r + cell*sqrt(2)/2, so the shortest feasible path is ~2*hypot(0.8-0.285, 1.2) + 0.57 m (grid adds <=9%)."""
import os
import sys

import numpy as np
from scipy.sparse import csgraph

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nav_eval_v3 import REF_CELL, reference, sign_test, wilson  # noqa: E402

xs = np.arange(-3, 3, 0.01)
wall = np.array([[0.0, 1.0, z] for z in xs if not (0.4 < z < 1.0)] * 3, np.float32)
ref = reference({"dense": wall, "C": np.array([[-0.8, 1.4, -0.5], [0.8, 1.4, -0.5]])}, 0.25)
fi = lambda x, z: ref["idx"][int((x - ref["lo"][0]) // REF_CELL), int((z - ref["lo"][1]) // REF_CELL)]
dist = csgraph.dijkstra(ref["G"], directed=False, indices=[fi(-0.8, -0.5)])[0, fi(0.8, -0.5)]
h = 0.25 + REF_CELL * np.sqrt(2) / 2
expect = 2 * np.hypot(0.8 - h, 1.2) + 2 * h
assert expect <= dist <= expect * 1.09, (dist, expect)
assert wilson(24, 40) == [0.4458, 0.7366] or abs(wilson(24, 40)[0] - 0.446) < 1e-3, wilson(24, 40)
assert abs(sign_test(5, 1) - 0.2188) < 1e-3
print(f"nav_eval_v3 contract test OK: geodesic {dist:.3f} m (analytic {expect:.3f} m), wilson(24/40)={wilson(24, 40)}")
