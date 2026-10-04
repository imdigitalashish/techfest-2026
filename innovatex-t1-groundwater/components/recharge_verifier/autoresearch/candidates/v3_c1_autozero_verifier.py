# NOT KEPT (v3-c1, 4 Oct 2026 10:36 IST): breaks pre-registered rule (eval_v1 4.347 > 4.292). See results.tsv.
"""C5 recharge-verifier — BASELINE implementation (the autoresearch loop edits only this file).

Input:  observed pit stage (m, ~1-min when wet), rain (mm per minute or per hour), structure registry
Output: list[RechargeEvent]-shaped dicts (see architecture/contracts/gwcontracts.py)

Method (baseline):
  1. Events: contiguous periods where stage > H_ON (2 cm), padded; merged if gaps < 3 h.
  2. Recession constant k (1/h): log-linear fit of stage on falling limbs with no rain in the previous
     30 min and stage between 5 cm and 95 % of the overflow stage. Per-event fit; falls back to the
     structure's running estimate when an event has no clean recession.
  3. Infiltrated volume = k * A * integral(h dt)   (linear-reservoir assumption).
  4. Inflow (stage-derived) = A * (h_end - h_start) + infiltrated + overflow_est; overflow_est from
     time spent at the spill stage x (rain prior inflow rate).
  5. Verdict: implausible (rise with < 1 mm rain, or inflow > 3x rain x catchment prior),
     no_inflow (>= 5 mm rain and max rise < 2 cm), clogged (k / k_as_built < 0.5), else verified.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

H_ON = 0.02
MERGE_GAP = pd.Timedelta(hours=3)
PAD = pd.Timedelta(minutes=30)
# ratchet switches (see autoresearch/results.tsv)
USE_WITHIN_FIT = True        # exp1: fit k within each contiguous recession limb (fixed-effects slope)
USE_RAIN_CONSISTENCY = True  # exp2: implausible only if stage-implied inflow exceeds what rain can explain
USE_JUMP_TEST = True         # exp3: flag one-minute stage jumps that rain in +-5 min cannot explain
USE_AUTO_ZERO = True         # v3-c1: subtract a slowly varying dry-floor baseline (sensor offset/drift)


def _auto_zero(stage: pd.Series) -> pd.Series:
    """Rolling 72-h 2nd percentile of 10-min medians = dry-floor reading; subtract it (never below 0)."""
    med = stage.resample("10min").median().dropna()
    if med.empty:
        return stage
    base = med.rolling("72h", min_periods=6).quantile(0.02)
    base = base.reindex(stage.index, method="ffill").fillna(float(med.iloc[: min(len(med), 432)].quantile(0.02)))
    return (stage - base).clip(lower=0.0)


def _events(stage: pd.Series) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    wet = stage[stage > H_ON]
    if wet.empty:
        return []
    t = wet.index
    breaks = np.where(np.diff(t.values).astype("timedelta64[m]").astype(int) > MERGE_GAP.total_seconds() / 60)[0]
    starts = [t[0]] + [t[i + 1] for i in breaks]
    ends = [t[i] for i in breaks] + [t[-1]]
    return [(s - PAD, e + PAD) for s, e in zip(starts, ends)]


def _fit_k(seg: pd.Series, rain_min: pd.Series, h_max: float) -> float | None:
    recent_rain = rain_min.reindex(seg.index, fill_value=0).rolling(30, min_periods=1).sum()
    ok = (seg > 0.05) & (seg < 0.95 * h_max) & (recent_rain <= 1e-9)
    s = seg[ok]
    if len(s) < 20:
        return None
    x = (s.index - s.index[0]).total_seconds() / 3600.0
    y = np.log(s.to_numpy())
    if USE_WITHIN_FIT:
        x = np.asarray(x)
        limb = np.concatenate([[0], np.cumsum(np.diff(x) > 0.1)])   # new limb after a >6-min gap
        num = den = 0.0
        for L in np.unique(limb):
            m = limb == L
            if m.sum() < 10:
                continue
            xc = x[m] - x[m].mean()
            num += float(np.sum(xc * (y[m] - y[m].mean())))
            den += float(np.sum(xc * xc))
        if den <= 0:
            return None
        slope = num / den
    else:
        slope = np.polyfit(x, y, 1)[0]
    return float(-slope) if slope < 0 else None


def verify(stage: pd.Series, rain_min: pd.Series, structure: dict) -> list[dict]:
    if USE_AUTO_ZERO:
        stage = _auto_zero(stage)
    A = structure["pit_area_m2"]
    hmax = structure["overflow_stage_m"]
    k_ref = structure["k_as_built_per_h"]
    k_run = k_ref
    out = []
    for i, (t0, t1) in enumerate(_events(stage)):
        seg = stage.loc[t0:t1]
        if len(seg) < 5:
            continue
        rain_mm = float(rain_min.loc[t0 - pd.Timedelta(hours=1):t1].sum())
        k = _fit_k(seg, rain_min, hmax)
        if k is not None:
            k_run = k
        k_use = k if k is not None else k_run
        dt_h = seg.index.to_series().diff().dt.total_seconds().fillna(60).to_numpy() / 3600.0
        integral = float(np.sum(np.clip(seg.to_numpy(), 0, None) * dt_h))
        infil = k_use * A * integral
        at_spill_h = float(np.sum(dt_h[seg.to_numpy() >= 0.98 * hmax]))
        prior_rate = structure["runoff_coeff"] * structure["catchment_m2"] * rain_mm / 1000.0
        dur_h = max((t1 - t0).total_seconds() / 3600.0, 1e-6)
        overflow = max(0.0, prior_rate / dur_h * at_spill_h - k_use * A * hmax * at_spill_h)
        inflow = max(0.0, A * (float(seg.iloc[-1]) - float(seg.iloc[0])) + infil + overflow)
        rise = float(seg.max() - seg.iloc[0])
        prior = structure["runoff_coeff"] * structure["catchment_m2"] * rain_mm / 1000.0
        ci = k_use / k_ref if k_ref else None
        if USE_RAIN_CONSISTENCY:
            implausible = (rain_mm < 0.1 and rise > 0.03) or inflow > 3.0 * prior + 0.15
        else:
            implausible = rain_mm < 1.0 or inflow > 3.0 * max(prior, 0.05)
        if USE_JUMP_TEST and not implausible:
            v = seg.to_numpy()
            dv = np.diff(v) * A                                          # m3 per sample step
            rr = rain_min.reindex(seg.index, fill_value=0).rolling(11, center=True, min_periods=1).sum().to_numpy()[1:]
            cap = 3.0 * structure["runoff_coeff"] * structure["catchment_m2"] * rr / 1000.0 + 0.15
            implausible = bool(np.any(dv > cap))
        if implausible:
            verdict = "implausible"
        elif ci is not None and ci < 0.5:
            verdict = "clogged"
        else:
            verdict = "verified"
        out.append({"structure_id": structure["structure_id"], "t_start": t0, "t_end": t1, "rain_mm": rain_mm,
                    "inflow_m3": inflow, "recharged_m3": infil, "overflow_m3": overflow, "k_per_h": k_use,
                    "clogging_index": ci, "verdict": verdict, "max_rise_m": rise})
    # rain with no response -> no_inflow events (daily windows with >= 5 mm and no detected event)
    daily = rain_min.resample("D").sum()
    for day, mm in daily[daily >= 5.0].items():
        d0, d1 = day, day + pd.Timedelta(days=1, hours=6)
        if not any(e["t_start"] <= d1 and e["t_end"] >= d0 for e in out):
            seg = stage.loc[d0:d1]
            rise = float(seg.max() - seg.min()) if len(seg) else 0.0
            if rise < H_ON:
                out.append({"structure_id": structure["structure_id"], "t_start": d0, "t_end": d1,
                            "rain_mm": float(mm), "inflow_m3": 0.0, "recharged_m3": 0.0, "overflow_m3": 0.0,
                            "k_per_h": None, "clogging_index": None, "verdict": "no_inflow", "max_rise_m": rise})
    return sorted(out, key=lambda e: e["t_start"])
