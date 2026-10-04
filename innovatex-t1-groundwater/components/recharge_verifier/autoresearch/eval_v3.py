"""FROZEN evaluator v3 for C5 — sensor realism on top of v2 (lead-owned; the loop must never edit it).

Adds, per pit, what the specified probe (DFRobot KIT0139, 0-5 m, 4-20 mA, overall accuracy 0.5 % FS =
+-25 mm; datasheet https://www.farnell.com/datasheets/3708809.pdf) and a 12-bit ADC can do to the stage:
  * constant offset ~ U(-25, +25) mm plus a linear drift of U(-10, +10) mm over the season
  * a 4-20 mA transmitter cannot report below 0 m: reading = max(0, h + offset + drift + noise)
  * quantisation to 2.1 mm (1.92 V span on a 3.3 V 12-bit ADC over 5 m)
plus everything in eval_v2 (drain law h^beta, beta ~ U(0.5, 1.5); gauge x lognormal(0.25)/day, 0-5 min lag).
Run: innovatex-t1-groundwater/.venv/bin/python innovatex-t1-groundwater/components/recharge_verifier/autoresearch/eval_v3.py [--split dev|holdout]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time

import numpy as np

import eval as v1  # noqa: E402
import eval_v2 as v2  # noqa: E402

QUANT_M = 0.0021


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev", choices=list(v1.SPLITS))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    seed = v1.SPLITS[a.split][2]
    v1.sim.make_fleet = v2._fleet_v2
    real_sim = v2._orig_simulate
    srng = np.random.default_rng(seed + 3000)

    def sim_with_sensor(p, rain_min, rng, noise_m=0.003):
        obs, truth = real_sim(p, rain_min, rng, noise_m)
        h_true = truth["h_m"].reindex(obs.index).to_numpy()
        off = srng.uniform(-0.025, 0.025)
        drift = srng.uniform(-0.010, 0.010)
        frac = np.linspace(0.0, 1.0, len(obs))
        noise = rng.normal(0.0, noise_m, len(obs))
        reading = np.maximum(0.0, h_true + off + drift * frac + noise)
        obs = obs.copy()
        obs["stage_m"] = np.round(reading / QUANT_M) * QUANT_M
        return obs, truth

    v1.sim.simulate_pit = sim_with_sensor
    real_verify = v1.verifier.verify
    gauge_rng = np.random.default_rng(seed + 2000)

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
    res["evaluator"] = "v3 (v2 + KIT0139-class offset/drift/quantisation)"
    res["runtime_s"] = round(time.time() - t, 1)
    print(json.dumps(res, indent=1))
    print(f"METRIC event_mdape={res['event_mdape']:.3f}")
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
