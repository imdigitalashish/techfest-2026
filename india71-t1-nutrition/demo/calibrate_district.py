"""Parameter-only helper: calibrate the SYNTHETIC simulator to one district's NFHS-5 under-5 wasting and stunting.

`components.cohort_simulator` is untouched (its defaults stay the reference synthetic district). In `simulate()`,
`wlz_mean` and `laz_mean_birth` enter every child-month's latent z additively (WLZ = wlz_mean + child offset + AR(1)
noise + episode offset; LAZ = laz_mean_birth - age decline + child offset + noise) and no random draw depends on them.
Shifting them by d therefore moves every true WLZ / LAZ by exactly d with the same random numbers, so the shift that
hits a target prevalence p is a quantile of the reference run: d = -2 - Q_p(true z over under-5 child-months).
Achieved values are then measured with the committed `components.cohort_simulator.calibrate.measure`.
Only wasting and stunting are calibrated; severe wasting is reported as achieved vs NFHS-5, not fitted.
"""

from __future__ import annotations

from dataclasses import replace

import numpy as np

from components.cohort_simulator.simulate import SimConfig
from components.growth_standards import who


def under5(truth_monthly):
    age_m = (truth_monthly.age_days / who.DAYS_PER_MONTH).astype(int)
    return truth_monthly[age_m < 60]


def district_overrides(reference_truth, wasted_pct: float, stunted_pct: float, base: SimConfig | None = None) -> dict:
    """SimConfig overrides so that true under-5 wasting / stunting equal the targets (percent, as NFHS-5 reports)."""
    base = base or SimConfig()
    u5 = under5(reference_truth)
    d_wlz = -2.0 - float(np.quantile(u5.true_wlz.to_numpy(), wasted_pct / 100.0))
    d_laz = -2.0 - float(np.quantile(u5.true_laz.to_numpy(), stunted_pct / 100.0))
    return {"wlz_mean": round(base.wlz_mean + d_wlz, 6), "laz_mean_birth": round(base.laz_mean_birth + d_laz, 6)}


def config(seed: int, overrides: dict) -> SimConfig:
    return replace(SimConfig(seed=seed), **overrides)
