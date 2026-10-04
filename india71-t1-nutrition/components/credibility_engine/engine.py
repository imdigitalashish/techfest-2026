"""Measurement credibility engine (spike candidate A).

Two levels, both computed from data Poshan Tracker already holds:
1. Record level — is this one measurement plausible? WHO implausibility flags plus
   longitudinal checks against the same child's history (height cannot shrink, weight
   cannot jump, three identical weights in a row).
2. Unit level — can we trust this Anganwadi centre's / worker's numbers? Indices that
   are hard to fake all at once: terminal-digit preference (weight, length), DOB heaping,
   dispersion of WHZ, share of flagged values, and *trajectory realism* — real children
   sometimes lose weight and measurement error sometimes makes length dip; copied-forward
   data almost never does.

Unit indices are robust-standardised against peers in the same district (median/MAD),
oriented so that higher = more suspicious, and combined into a credibility in [0, 1].
No labels are needed (in reality nobody labels fabricated data); the simulator's ground
truth is used only to evaluate.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from components.growth_standards import who

# Index weights (the auto-research loop tunes these and the index set; eval.py is frozen)
INDEX_WEIGHTS = {
    "dps_weight": 1.0,
    "dps_length": 1.0,
    "dob_heaping": 0.5,
    "sd_whz_dev": 1.0,
    "pct_flagged": 0.5,
    "p_nonneg_dweight": 1.5,
    "p_nonneg_dlength": 1.5,
    "low_wasting_vs_peers": 0.5,
}


def digit_preference_score(values: pd.Series) -> float:
    """SMART-style DPS on the first decimal: 100*sqrt(chi2/(n*df)); 0 = uniform digits."""
    v = values.dropna()
    if len(v) < 20:
        return np.nan
    d = np.rint((v.to_numpy() * 10) % 10).astype(int) % 10
    obs = np.bincount(d, minlength=10)
    exp = len(d) / 10
    chi2 = ((obs - exp) ** 2 / exp).sum()
    return float(100 * np.sqrt(chi2 / (len(d) * 9)))


def add_zscores(meas: pd.DataFrame) -> pd.DataFrame:
    m = meas.copy()
    m["age_days"] = (m.measured_on - m.dob).dt.days
    z = who.compute(m)
    return pd.concat([m, z], axis=1)


def record_checks(mz: pd.DataFrame) -> pd.DataFrame:
    """Per-event findings. Input: measurements with z-scores (add_zscores). Output columns:
    event_id, findings (list[str]), usable (bool), confidence (float)."""
    m = mz.sort_values(["child_key", "measured_on"]).copy()
    g = m.groupby("child_key", sort=False)
    lh_std = who.standardise_length(m.age_days, m.length_height_cm, m.measure_position)
    m["lh_std"] = lh_std
    prev_lh = g.lh_std.shift(1)
    prev_w = g.weight_kg.shift(1)
    prev2_w = g.weight_kg.shift(2)
    dt = (m.measured_on - g.measured_on.shift(1)).dt.days
    findings = [[] for _ in range(len(m))]
    rules = {
        "WHO_FLAG": (m[[f"flag_{c}" for c in ("waz", "lhaz", "wlhz")]].any(axis=1), "reject"),
        "HEIGHT_DECREASE": ((prev_lh - m.lh_std) > 1.5, "reject"),
        "WEIGHT_JUMP": (((m.weight_kg - prev_w).abs() > np.maximum(1.5, 0.25 * prev_w)) & (dt <= 45), "reject"),
        "EXACT_REPEAT_3": ((m.weight_kg == prev_w) & (prev_w == prev2_w), "warn"),
        "POSITION_AGE_MISMATCH": (((m.age_days < 731) & (m.measure_position == "standing"))
                                  | ((m.age_days >= 731) & (m.measure_position == "recumbent")), "info"),
    }
    reject = np.zeros(len(m), bool)
    conf = np.ones(len(m))
    for code, (mask, sev) in rules.items():
        mask = mask.fillna(False).to_numpy()
        for i in np.nonzero(mask)[0]:
            findings[i].append(code)
        if sev == "reject":
            reject |= mask
            conf[mask] *= 0.1
        elif sev == "warn":
            conf[mask] *= 0.6
    return pd.DataFrame({"event_id": m.event_id.to_numpy(), "findings": findings, "usable": ~reject,
                         "confidence": conf}, index=m.index)


def unit_indices(mz: pd.DataFrame, unit: str = "awc_code") -> pd.DataFrame:
    m = mz.sort_values(["child_key", "measured_on"])
    g = m.groupby("child_key", sort=False)
    m = m.assign(dw=g.weight_kg.diff(), dl=g.length_height_cm.diff(), same_unit=g[unit].shift(1) == m[unit])
    pairs = m[m.same_unit & m.dw.notna()]
    dob_day = m.dob.dt.day
    rows = []
    for uid, u in m.groupby(unit):
        p = pairs[pairs[unit] == uid]
        whz = u.wlhz.where(~u.flag_wlhz)
        rows.append(dict(
            unit_id=uid, n_measurements=len(u),
            dps_weight=digit_preference_score(u.weight_kg),
            dps_length=digit_preference_score(u.length_height_cm),
            dob_heaping=float((dob_day[u.index] == 1).mean()),
            sd_whz=float(whz.std()),
            pct_flagged=float(u[["flag_waz", "flag_lhaz", "flag_wlhz"]].any(axis=1).mean()),
            p_nonneg_dweight=float((p.dw >= 0).mean()) if len(p) else np.nan,
            p_nonneg_dlength=float((p.dl >= 0).mean()) if len(p) else np.nan,
            wasting_prev=float((whz < -2).mean()),
        ))
    return pd.DataFrame(rows)


def _robust_z(x: pd.Series) -> pd.Series:
    med = x.median()
    mad = 1.4826 * (x - med).abs().median()
    return (x - med) / (mad if mad and np.isfinite(mad) and mad > 1e-9 else (x.std() or 1.0))


def score_units(ix: pd.DataFrame, weights: dict | None = None) -> pd.DataFrame:
    w = weights or INDEX_WEIGHTS
    s = ix.copy()
    s["sd_whz_dev"] = (s.sd_whz - 1.0).abs()  # WHO/UNICEF 2019: SD of WHZ expected near 1
    s["low_wasting_vs_peers"] = -s.wasting_prev
    susp = pd.DataFrame({k: _robust_z(s[k]).clip(lower=0) for k in w}).fillna(0)
    total = sum(susp[k] * v for k, v in w.items()) / sum(w.values())
    s["suspicion"] = total
    s["credibility"] = 1 / (1 + np.exp(2.0 * (total - 1.5)))
    s["band"] = np.select([s.n_measurements < 30, s.credibility >= 0.7, s.credibility >= 0.4],
                          ["insufficient_data", "high", "medium"], "low")
    s["recommended_action"] = np.select([s.band == "low", s.band == "medium"],
                                        ["remeasure_sample", "supportive_supervision"], "none")
    return s


def assess(measurements: pd.DataFrame, unit: str = "awc_code", weights: dict | None = None):
    mz = add_zscores(measurements)
    rec = record_checks(mz)
    good = mz.loc[rec.index[rec.usable.to_numpy()]]
    units = score_units(unit_indices(good, unit), weights)
    return mz, rec, units
