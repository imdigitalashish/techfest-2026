"""Achieved vs target calibration of the SYNTHETIC cohort (true latent values, before measurement error).

Targets (verified, research/sources/L5-growth-epi.md): Mertens et al., Nature 2023 (ki consortium) —
South Asia at-birth wasting 18.9%; South Asia cumulative wasting incidence by 24 months 52.2%;
pooled recovery within 90 days 71.1% (lower in South Asia). NFHS-5 under-5 prevalence targets are
added when verified (research/sources/L3-nfhs5.md).
Run: .venv/bin/python -m components.cohort_simulator.calibrate
"""

import json

import numpy as np

from components.cohort_simulator.simulate import SimConfig, simulate
from components.growth_standards import who

TARGETS = {"at_birth_wasting_SA": 0.189, "cum_incidence_24m_SA": 0.522, "recovery_90d_pooled": 0.711}


def measure(cfg: SimConfig | None = None) -> dict:
    out = simulate(cfg)
    t = out["truth_monthly"]
    t = t.assign(age_m=(t.age_days / who.DAYS_PER_MONTH).astype(int), wasted=t.true_wlz < -2)
    u5 = t[t.age_m < 60]
    res = {
        "n_children": int(out["children"].shape[0]),
        "n_measurement_events": int(out["measurements"].shape[0]),
        "wasting_prev_u5": round(float(u5.wasted.mean()), 3),
        "stunting_prev_u5": round(float((u5.true_laz < -2).mean()), 3),
        "severe_wasting_prev_u5": round(float((u5.true_wlz < -3).mean()), 3),
        "wasting_prev_0_5m": round(float(u5[u5.age_m < 6].wasted.mean()), 3),
        "at_birth_wasting": round(float(t[t.age_m == 0].wasted.mean()), 3),
    }
    # cumulative incidence by 24 m among children observed every month from birth to 24 m
    full = t[t.age_m < 24].groupby("child_key").agg(n=("age_m", "nunique"), ever=("wasted", "max"))
    full = full[full.n >= 24]
    res["cum_incidence_24m"] = round(float(full.ever.mean()), 3) if len(full) else None
    res["n_children_birth_to_24m"] = int(len(full))
    # recovery within 90 days: episodes starting at a month with wasted after not wasted
    t = t.sort_values(["child_key", "age_m"])
    w = t.groupby("child_key").wasted
    onset = t.wasted & ~w.shift(1, fill_value=False)
    rec = []
    tw = t.wasted.to_numpy()
    keys = t.child_key.to_numpy()
    for i in np.nonzero(onset.to_numpy())[0]:
        ahead = [j for j in range(i + 1, min(i + 4, len(t))) if keys[j] == keys[i]]
        if len(ahead) == 3:
            rec.append(any(not tw[j] for j in ahead))
    res["recovery_90d"] = round(float(np.mean(rec)), 3) if rec else None
    res["targets"] = TARGETS
    res["synthetic"] = True
    return res


if __name__ == "__main__":
    print(json.dumps(measure()))
