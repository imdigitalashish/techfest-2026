"""FROZEN evaluator v2 for C5 — model-mismatch stress test (lead-owned; the loop must never edit it).

Same splits, fleets and metrics as eval.py, plus two realities the v1 simulator hides:
  1. Drain law mismatch: each pit drains as outflow ∝ h^beta with beta ~ U(0.5, 1.5)
     (0.5 = orifice-like, 1 = linear reservoir assumed by the baseline verifier, 1.5 = side-wall dominated).
  2. Imperfect rain gauge: the verifier sees rain multiplied by a per-day lognormal factor (sigma 0.25)
     and shifted by a fixed 0-5 min lag per pit (gauge on a neighbouring roof).
Run: innovatex-t1-groundwater/.venv/bin/python innovatex-t1-groundwater/components/recharge_verifier/autoresearch/eval_v2.py [--split dev|holdout]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time

import numpy as np

import eval as v1  # noqa: E402  (same folder; reuses the frozen v1 machinery)

_orig_make_fleet = v1.sim.make_fleet
_orig_simulate = v1.sim.simulate_pit


def _fleet_v2(n, seed, start, end):
    fleet = _orig_make_fleet(n, seed, start, end)
    r = np.random.default_rng(seed + 1000)
    for p in fleet:
        p.drain_exponent = float(r.uniform(0.5, 1.5))
    return fleet


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev", choices=list(v1.SPLITS))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    v1.sim.make_fleet = _fleet_v2
    real_verify = v1.verifier.verify
    gauge_rng = np.random.default_rng(v1.SPLITS[a.split][2] + 2000)

    def verify_with_gauge(stage, rain_min, structure):
        days = rain_min.index.floor("D")
        factor = np.exp(gauge_rng.normal(0, 0.25, len(days.unique())))
        fmap = dict(zip(days.unique(), factor))
        lag = int(gauge_rng.integers(0, 6))
        observed = (rain_min * days.map(fmap).to_numpy()).shift(lag, fill_value=0.0)
        return real_verify(stage, observed, structure)

    v1.verifier.verify = verify_with_gauge
    t = time.time()
    res = v1.run(a.split)
    res["evaluator"] = "v2 (drain-law mismatch + imperfect gauge)"
    res["runtime_s"] = round(time.time() - t, 1)
    print(json.dumps(res, indent=1))
    print(f"METRIC event_mdape={res['event_mdape']:.3f}")
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
