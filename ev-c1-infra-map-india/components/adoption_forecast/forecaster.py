"""C9 adoption_forecast — the ONLY file the auto-research loop edits.
forecast(bev, allv) -> {state: BEV registrations forecast for the year after the last column}
  bev, allv: DataFrames (index = VAHAN state label, columns = calendar years as int, values = registrations); only years <= origin.
"""
import numpy as np

PARAMS = {'method': 'share_logit', 'k': 2, 'w': 0.5, 'phi': 0.5}


def _logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def forecast(bev, allv):
    p = PARAMS
    yrs = sorted(bev.columns)
    last, prev = bev[yrs[-1]], bev[yrs[-2]]
    if p["method"] == "naive":
        f = last
    elif p["method"] == "growth":
        g = (last + 1) / (prev + 1) - 1
        f = last * (1 + p.get("phi", 1.0) * g)
    elif p["method"] == "pooled_growth":
        g_s = (last + 1) / (prev + 1) - 1
        g_n = last.sum() / prev.sum() - 1
        f = last * (1 + p.get("phi", 1.0) * (p["w"] * g_s + (1 - p["w"]) * g_n))
    elif p["method"] == "share_logit":
        k = p.get("k", 3)
        ys = yrs[-k:]
        share = (bev[ys] + 0.5) / (allv[ys] + 1)
        L = _logit(share.to_numpy())
        x = np.arange(k) - (k - 1) / 2
        slope_s = (L * x).sum(1) / (x ** 2).sum()
        nat = _logit((bev[ys].sum() + 0.5) / (allv[ys].sum() + 1)).to_numpy()
        slope_n = (nat * x).sum() / (x ** 2).sum()
        slope = p.get("phi", 1.0) * (p["w"] * slope_s + (1 - p["w"]) * slope_n)
        nxt = L[:, -1] + slope
        tot_growth = allv[yrs[-1]].sum() / allv[yrs[-2]].sum()
        f = (1 / (1 + np.exp(-nxt))) * allv[yrs[-1]].to_numpy() * tot_growth
        return {s: float(v) for s, v in zip(bev.index, f)}
    else:
        raise ValueError(p["method"])
    return {s: float(v) for s, v in f.items()}


# ---- v2: monthly data (VAHAN State x Month Wise) -------------------------------------------------
PARAMS_M = {'method': 'share_logit', 'k': 2, 'w': 0.5, 'phi': 0.5}


def _share_next(bev_m, all_m, k, w, phi):
    """Pooled logit trend of the trailing-12-month EV share, sampled at yearly lags (k windows)."""
    wins = [(bev_m.iloc[:, bev_m.shape[1] - 12 * (i + 1): bev_m.shape[1] - 12 * i].sum(1),
             all_m.iloc[:, all_m.shape[1] - 12 * (i + 1): all_m.shape[1] - 12 * i].sum(1)) for i in range(k)][::-1]
    L = np.array([_logit(((b + 0.5) / (a + 1)).to_numpy()) for b, a in wins]).T  # states x k
    x = np.arange(k) - (k - 1) / 2
    slope_s = (L * x).sum(1) / (x ** 2).sum()
    nat = np.array([_logit((b.sum() + 0.5) / (a.sum() + 1)) for b, a in wins])
    slope_n = (nat * x).sum() / (x ** 2).sum()
    nxt = L[:, -1] + phi * (w * slope_s + (1 - w) * slope_n)
    a_last, a_prev = wins[-1][1], wins[-2][1]
    return pd.Series((1 / (1 + np.exp(-nxt))) * a_last.to_numpy() * (a_last.sum() / a_prev.sum()), index=bev_m.index)


def forecast_12m(bev_m, all_m, params=None):
    """Next-12-month BEV registrations per state from monthly history up to the origin (inclusive)."""
    p = params or PARAMS_M
    last12, prev12 = bev_m.iloc[:, -12:].sum(1), bev_m.iloc[:, -24:-12].sum(1)
    m = p["method"]
    if m == "naive12":
        return last12
    if m == "pooled_growth":
        g_s = (last12 + 1) / (prev12 + 1) - 1
        g_n = last12.sum() / prev12.sum() - 1
        return last12 * (1 + p["phi"] * (p["w"] * g_s + (1 - p["w"]) * g_n))
    if m == "share_logit":
        return _share_next(bev_m, all_m, p.get("k", 2), p["w"], p["phi"])
    if m == "ensemble":
        fs = [forecast_12m(bev_m, all_m, q) for q in p["members"]]
        wts = p.get("weights") or [1 / len(fs)] * len(fs)
        return sum(wt * f for wt, f in zip(wts, fs))
    raise ValueError(m)


import pandas as pd  # noqa: E402  (used by the monthly functions above)
