# NOT KEPT (v2-exp3, 4 Oct 2026 09:40 IST): eval_v2 dev 4.855 but eval_v1 dev 4.693 vs 3.902 kept -> breaks keep rule. Saved for resume; see results.tsv.
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
USE_DRAIN_EXPONENT = True    # v2-exp1: per-structure drain law q = k*A*h_ref*(h/h_ref)^beta, beta from recession rates
H_REF = 0.5


def _rate_windows(seg: pd.Series, rain_min: pd.Series, h_max: float, win: int = 30):
    """(h_mid, -dh/dt) from non-overlapping 30-min windows on clean recession limbs."""
    recent_rain = rain_min.reindex(seg.index, fill_value=0).rolling(30, min_periods=1).sum()
    ok = (seg > 0.05) & (seg < 0.95 * h_max) & (recent_rain <= 1e-9)
    s = seg[ok]
    if len(s) < win:
        return np.empty(0), np.empty(0)
    x = (s.index - s.index[0]).total_seconds().to_numpy() / 3600.0
    y = s.to_numpy()
    limb = np.concatenate([[0], np.cumsum(np.diff(x) > 0.1)])
    hs, rs = [], []
    for L in np.unique(limb):
        idx = np.where(limb == L)[0]
        for j in range(0, len(idx) - win + 1, win):
            w = idx[j:j + win]
            slope = np.polyfit(x[w], y[w], 1)[0]
            if slope < 0:
                hs.append(float(np.mean(y[w])))
                rs.append(float(-slope))
    return np.asarray(hs), np.asarray(rs)


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


def _fit_k_beta(seg: pd.Series, rain_min: pd.Series, h_max: float, beta: float) -> float | None:
    """Within-limb (fixed-effects) fit of z(t) = h^(1-beta)/(1-beta) (ln h if beta = 1); dz/dt = -k*H_REF^(1-beta)."""
    recent_rain = rain_min.reindex(seg.index, fill_value=0).rolling(30, min_periods=1).sum()
    ok = (seg > 0.05) & (seg < 0.95 * h_max) & (recent_rain <= 1e-9)
    s = seg[ok]
    if len(s) < 20:
        return None
    x = (s.index - s.index[0]).total_seconds().to_numpy() / 3600.0
    h = s.to_numpy()
    z = np.log(h) if abs(beta - 1.0) < 1e-6 else h ** (1.0 - beta) / (1.0 - beta)
    limb = np.concatenate([[0], np.cumsum(np.diff(x) > 0.1)])
    num = den = 0.0
    for L in np.unique(limb):
        m = limb == L
        if m.sum() < 10:
            continue
        xc = x[m] - x[m].mean()
        num += float(np.sum(xc * (z[m] - z[m].mean())))
        den += float(np.sum(xc * xc))
    if den <= 0:
        return None
    slope = num / den
    return float(-slope / H_REF ** (1.0 - beta)) if slope < 0 else None


def verify(stage: pd.Series, rain_min: pd.Series, structure: dict) -> list[dict]:
    A = structure["pit_area_m2"]
    hmax = structure["overflow_stage_m"]
    k_ref = structure["k_as_built_per_h"]
    k_run = k_ref
    beta = 1.0
    pool_h: list[float] = []
    pool_r: list[float] = []
    out = []
    for i, (t0, t1) in enumerate(_events(stage)):
        seg = stage.loc[t0:t1]
        if len(seg) < 5:
            continue
        rain_mm = float(rain_min.loc[t0 - pd.Timedelta(hours=1):t1].sum())
        dt_h = seg.index.to_series().diff().dt.total_seconds().fillna(60).to_numpy() / 3600.0
        hpos = np.clip(seg.to_numpy(), 0, None)
        if USE_DRAIN_EXPONENT:
            hw, rw = _rate_windows(seg, rain_min, hmax)
            pool_h += hw.tolist()
            pool_r += rw.tolist()
            beta = 1.0
            if len(pool_h) >= 8 and np.ptp(np.log(pool_h)) >= 0.7:
                lx, ly = np.log(pool_h), np.log(pool_r)
                b, a0 = np.polyfit(lx, ly, 1)
                resid = ly - (b * lx + a0)
                se = float(np.sqrt(np.sum(resid ** 2) / max(len(lx) - 2, 1) / np.sum((lx - lx.mean()) ** 2)))
                if abs(b - 1.0) > 2.0 * se:          # v2-exp3: non-linear drain only when the data demand it
                    beta = float(np.clip(b, 0.3, 2.0))
            if beta == 1.0:
                k = _fit_k(seg, rain_min, hmax)
                if k is not None:
                    k_run = k
                k_use = k if k is not None else k_run
                infil = float(k_use * A * np.sum(hpos * dt_h))
            else:
                k = _fit_k_beta(seg, rain_min, hmax, beta)
                if k is not None:
                    k_run = k
                k_use = k if k is not None else k_run
                infil = float(np.sum(k_use * A * H_REF * (hpos / H_REF) ** beta * dt_h))
        else:
            k = _fit_k(seg, rain_min, hmax)
            if k is not None:
                k_run = k
            k_use = k if k is not None else k_run
            integral = float(np.sum(hpos * dt_h))
            infil = k_use * A * integral
        at_spill_h = float(np.sum(dt_h[seg.to_numpy() >= 0.98 * hmax]))
        prior_rate = structure["runoff_coeff"] * structure["catchment_m2"] * rain_mm / 1000.0
        dur_h = max((t1 - t0).total_seconds() / 3600.0, 1e-6)
        q_at_spill = k_use * A * (H_REF * (hmax / H_REF) ** beta if USE_DRAIN_EXPONENT else hmax)
        overflow = max(0.0, prior_rate / dur_h * at_spill_h - q_at_spill * at_spill_h)
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
